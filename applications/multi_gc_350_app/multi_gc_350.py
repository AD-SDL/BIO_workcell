#!/usr/bin/env python3

from pathlib import Path

# from rpl_wei.wei_workcell_base import WEI
from tools.gladier_flow.growth_curve_gladier_flow import c2_flow
from pathlib import Path
from tools.hudson_solo_auxillary.hso_functions import package_hso
from tools.hudson_solo_auxillary import solo_step1, solo_step2, solo_step3
from rpl_wei import Experiment
import time


def main():

    # Workflow paths (TODO: perhaps not hard coded :) )

    wf_path_1 = Path(
        "/home/rpl/workspace/BIO_workcell/applications/applications/growth_app/workflows/create_plate_T0.yaml"
    )
    wf_path_2 = Path(
        "/home/rpl/workspace/BIO_workcell/applications/applications/growth_app/workflows/read_plate_T12.yaml"
    )

    #Creates a WEI Experiment at the 8000 port and registers the experiment 
    exp = Experiment("127.0.0.1", "8000", "Multi_GC_350")
    exp.register_exp()

    # TODO: Excel parsing with checks on input values
        # - are the lists equal length
        # - format lists for payload
        # - separate variable for number of assay plates to create

    num_assay_plates = 12

    # Initial payload setup
    payload = {
        "temp": 37.0, #a float value setting the temperature of the Liconic Incubator (in Celsius) 
        "humidity": 95.0, # a float value setting the humidity of the Liconic Incubator
        "shaker_speed": 30, #an integer value setting the shaker speed of the Liconic Incubator
        # "stacker": 1, # an integer value specifying which stacker a well plate should be used in (Preferable to use "incubation_plate_id" : plate_id, where plate_id is an integer 1-88 - stacker and slot will be autocalculated)
        # "slot": 2, # an integer value specifying which slot a well plate should be used in (Preferable to use "incubation_plate_id" : plate_id, where plate_id is an integer 1-88 - stacker and slot will be autocalculated)
        "treatment": ["col1" ,"col2", "col3", "col4", "col4","col5" ,"col6", "col7", "col8", "col9", "col10", "col11", "col12"],  # string of treatment name. Ex. "col1", "col2"
        "culture_column": [1,2,3,4,5,6,7,8,9,10,11,12],  # what column of the culture stock plate to use for each assay plate
        "culture_dil_column": [1,2,3,4,5,6,7,8,9,10,11,12],  # int of dilution column for 1:10 culture dilutions. Ex. 1, 2, 3, etc.
        "media_start_column": [1,3,5,7,9,11,1,3,5,7,9,11],  # int of column to draw media from (requires 2 columns, 1 means columns 1 and 2) Ex. 1, 3, 5, etc.
        "treatment_dil_half": [1,2,1,2,1,2,1,2,1,2,1,2],  #  int of which plate half to use for treatment serial dilutions. Options are 1 or 2.
        "tip_box_position": "1", # string of an integer 1-8 that identifies the position of the tip box when it is being refilled
    }

    # Lopping to create assay plates

    for i in range(num_assay_plates): 

        payload["current_assay_plate_num"] = i

        # generate and package hso files (3 hso files per assay plate creation)   # TODO remove i from the function args now
        exp.events.log_local_compute("package_hso")  # Q: Do we need this??
        hso_1, hso_1_lines, hso_1_basename = package_hso(
            solo_step1.generate_hso_file, payload, i, "/home/rpl/wei_temp/solo_temp1.hso"
        )
        hso_2, hso_2_lines, hso_2_basename = package_hso(
            solo_step2.generate_hso_file, payload, i, "/home/rpl/wei_temp/solo_temp2.hso"
        )
        hso_3, hso_3_lines, hso_3_basename = package_hso(
            solo_step3.generate_hso_file, payload, i, "/home/rpl/wei_temp/solo_temp3.hso"
        )

        # Add the HSO Packages to the payload to send to the Hudson Solo
        payload["hso_1"] = hso_1
        payload["hso_1_lines"] = hso_1_lines
        payload["hso_1_basename"] = hso_1_basename

        payload["hso_2"] = hso_2
        payload["hso_2_lines"] = hso_2_lines
        payload["hso_2_basename"] = hso_2_basename

        payload["hso_3"] = hso_3
        payload["hso_3_lines"] = hso_3_lines
        payload["hso_3_basename"] = hso_3_basename

        # TODO: Do we want to set up tip box on deck for first run??
        # if run# % 2 == 0 then replace tip box and serial dilution plate (by hand or if we want to use gripper on the robot)

        # Run the T0 Workflow on the Registered WEI Experiment with the payload specified above
        flow_info = exp.run_job(wf_path_1.resolve(), payload=payload, simulate=False)    

        # Pinging the status of the T0 Workflow sent to the WEI Experiment every 3 seconds  # TODO: Do we need this???
        flow_status = exp.query_job(flow_info["job_id"])
        while flow_status["status"] != "finished" and flow_status["status"] != "failure":
            flow_status = exp.query_job(flow_info["job_id"])
            time.sleep(3)

        # TODO: AT THIS POINT: plate is just placed in incubator (timestamp)

        # Receiving the Results of the now completed T0 Workflow, Creating a Path of the Run Directory, and printing the Run Information
        run_info = flow_status["result"]
        run_info["run_dir"] = Path(run_info["run_dir"])
        print(run_info)

        # Accessing the T0 Reading results file path from the Hidex 
        hidex_file_path = run_info["hist"]["run Hidex"]["action_msg"]

        # Formatting the File Path from Windows to be compatible with Linux file directory settings and creating a Path
        hidex_file_path = hidex_file_path.replace('\\', '/')
        hidex_file_path = hidex_file_path.replace("C:/", "/C/")
        flow_title = Path(hidex_file_path) #Path(run_info["hist"]["run_assay"]["step_response"])

        # Accessing the File Name
        fname = flow_title.name

        # Accessing the File Path
        flow_title = flow_title.parents[0]

        # TODO: Get globus things working again 
        # #Uploading the Hidex Data to the Globus client and portal. The arguments in the function are the strings of the experiment name (exp_name), plate number (plate_n), time uploaded (time), the flow_title (local_path), and file name (fname), and the WEI Experiment Object).
        # c2_flow(exp_name = "T0_Reading", plate_n = "1", time = str(time.strftime("%H_%M_%S", time.localtime())), local_path=flow_title, fname = fname, exp = exp)

        # END PLATE CREATION LOOP

    # Incubate for 12 hours
    print("Incubating plate for 12 hours")
    time.sleep(43200)    # TODO: Change this so we don't have to manually 

    # BEGIN READ PLATE T12 LOOP
    for i in range(num_assay_plates): 
        # Run the T12 Workflow on the Registered WEI Experiment with the payload specified above to read the plate after the 12 hour wait
        flow_info = exp.run_job(wf_path_2.resolve(), payload=payload, simulate=False)
        
        # Pinging the status of the T0 Workflow sent to the WEI Experiment
        flow_status = exp.query_job(flow_info["job_id"])
        #Periodically checking the status every 3 seconds of the T0 Workflow until it is finished
        while(flow_status["status"] != "finished" and flow_status["status"] != "failure"):
            flow_status = exp.query_job(flow_info["job_id"])
            time.sleep(3)
        
        # Receiving the Results of the now completed T0 Workflow, Creating a Path of the Run Directory, and printing the Run Information
        run_info = flow_status["result"]
        run_info["run_dir"] = Path(run_info["run_dir"])
        print(run_info)

        # Accessing the T12 Reading results file path from the Hidex 
        hidex_file_path = run_info["hist"]["run Hidex"]["action_msg"]
        # Formatting the File Path from Windows to be compatible with Linux file directory settings and creating a Path
        hidex_file_path = hidex_file_path.replace('\\', '/')
        hidex_file_path = hidex_file_path.replace("C:/", "/C/")
        flow_title = Path(hidex_file_path) #Path(run_info["hist"]["run_assay"]["step_response"])
        # Accessing the File Name
        fname = flow_title.name
        # Accessing the File Path
        flow_title = flow_title.parents[0]
        
        #Uploading the Hidex Data to the Globus client and portal. The arguments in the function are the strings of the experiment name (exp_name), plate number (plate_n), time uploaded (time), the flow_title (local_path), and file name (fname), and the WEI Experiment Object).
        #Experiment name is T12_Reading to easily distinguish from the initial T0 Results in a Globus Portal Search
        c2_flow(exp_name = "T12_Reading", plate_n = "1", time = str(time.strftime("%H_%M_%S", time.localtime())), local_path=flow_title, fname = fname, exp = exp)


if __name__ == "__main__":
    main()