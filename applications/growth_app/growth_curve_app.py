#!/usr/bin/env python3

from pathlib import Path

# from rpl_wei.wei_workcell_base import WEI
import wei
from tools.gladier_flow.growth_curve_gladier_flow import c2_flow
from pathlib import Path
from tools.hudson_solo_auxillary.hso_functions import package_hso
from tools.hudson_solo_auxillary import solo_step1, solo_step2, solo_step3
# from rpl_wei import Experiment

import time

# The main script for running a single-cell plate growth assay. 
def main():
    #Accessing the paths for the T0 Workflow and the T12 workflow. 
    #The Paths will need to be changed if the corresponding Yaml file locations are changed

    # directory paths
    bio_workcell_path = Path(__file__).parent.parent.parent
    app_dir = bio_workcell_path / "applications" / "growth_app"
    wf_dir = app_dir / "workflows"
    

    # workflow paths
    T0_wf_path = wf_dir / "create_plate_T0.yaml"
    T12_wf_path = wf_dir / "read_plate_T12.yaml"

    # wf_path_1 = Path(
    #     "/home/rpl/workspace/BIO_workcell/applications/applications/growth_app/workflows/create_plate_T0.yaml"
    # )
    # wf_path_2 = Path(
    #     "/home/rpl/workspace/BIO_workcell/applications/applications/growth_app/workflows/read_plate_T12.yaml"
    # )

    #Creates a WEI Experiment at the 8000 port and registers the experiment with the title Growth_Curve
 
    exp = wei.ExperimentClient(
        server_host = "127.0.0.1",
        server_port = "8000",
        experiment_name = "Growth_App",
        description="Single plate growth curve assay."
    )
    #exp.register_exp()

    #Generate the payload for the T0 and T12 readings. The T0 and T12 Yaml files (at the position paths above) and hso_packages for the Hudson Solo (created below) will use the following values in the workflow
    payload = {
        "temp": 37.0, #a float value setting the temperature of the Liconic Incubator (in Celsius) 
        "humidity": 95.0, # a float value setting the humidity of the Liconic Incubator
        "shaker_speed": 30, #an integer value setting the shaker speed of the Liconic Incubator
        "stacker": 1, # an integer value specifying which stacker a well plate should be used in (Preferable to use "incubation_plate_id" : plate_id, where plate_id is an integer 1-88 - stacker and slot will be autocalculated)
        "slot": 2, # an integer value specifying which slot a well plate should be used in (Preferable to use "incubation_plate_id" : plate_id, where plate_id is an integer 1-88 - stacker and slot will be autocalculated)
        "treatment": "col1",  # string of treatment name. Ex. "col1", "col2"
        "culture_column": 4,  # int of cell culture column. Ex. 1, 2, 3, etc.
        "culture_dil_column": 1,  # int of dilution column for 1:10 culture dilutions. Ex. 1, 2, 3, etc.
        "media_start_column": 1,  # int of column to draw media from (requires 2 columns, 1 means columns 1 and 2) Ex. 1, 3, 5, etc.
        "treatment_dil_half": 1,  #  int of which plate half to use for treatment serial dilutions. Options are 1 or 2.
        "tip_box_position": "3", # string of an integer 1-8 that identifies the position of the tip box when it is being refilled
    }

    # Creating HSO Packages to send liquid handling protocols to the Hudson Solo.
    # There are 3 separate hso files added because Hudson Solo caps the amount of steps per protocol.
    exp.events.log_local_compute("package_hso")
    hso_1, hso_1_lines, hso_1_basename = package_hso(
        solo_step1.generate_hso_file, payload, "/home/rpl/wei_temp/solo_temp1.hso"
    )
    hso_2, hso_2_lines, hso_2_basename = package_hso(
        solo_step2.generate_hso_file, payload, "/home/rpl/wei_temp/solo_temp2.hso"
    )
    hso_3, hso_3_lines, hso_3_basename = package_hso(
        solo_step3.generate_hso_file, payload, "/home/rpl/wei_temp/solo_temp3.hso"
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

    # Run the T0 Workflow on the Registered WEI Experiment with the payload specified above
    run_info = exp.start_run(T0_wf_path.resolve(), payload=payload, simulate=False)

    # Pinging the status of the T0 Workflow sent to the WEI Experiment
    # flow_status = exp.query_job(flow_info["job_id"])
    # #Periodically checking the status every 3 seconds of the T0 Workflow until it is finished
    # while flow_status["status"] != "finished" and flow_status["status"] != "failure":
    #     flow_status = exp.query_job(flow_info["job_id"])
    #     time.sleep(3)

    # Receiving the Results of the now completed T0 Workflow, Creating a Path of the Run Directory, and printing the Run Information
    # run_info = flow_status["result"]
    # run_info["run_dir"] = Path(run_info["run_dir"])
    # print(run_info)

    # Accessing the T0 Reading results file path from the Hidex # TODO: How do we do this now?
    hidex_file_name = run_info["hist"]["run Hidex"]["action_msg"]
    output_dir = Path.home() / "runs" / run_info["experiment_id"]
    output_dir.mkdir(parents=True, exist_ok=True)
    exp.get_wf_result_file(run_id=run_info["run_id"], filename=hidex_file_name, output_filepath=output_dir / hidex_file_name)
    # Formatting the File Path from Windows to be compatible with Linux file directory settings and creating a Path
    # hidex_file_path = hidex_file_path.replace('\\', '/')
    # hidex_file_path = hidex_file_path.replace("C:/", "/C/")
    # flow_title = Path(hidex_file_path) #Path(run_info["hist"]["run_assay"]["step_response"])
    # Accessing the File Name
    # fname = flow_title.name
    # print("FILE NAME")
    # print(fname)
    # # Accessing the File Path
    # flow_title = flow_title.parents[0]
    # print("FILE PATH")
    # print(flow_title)
    

    #Uploading the Hidex Data to the Globus client and portal. The arguments in the function are the strings of the experiment name (exp_name), plate number (plate_n), time uploaded (time), the flow_title (local_path), and file name (fname), and the WEI Experiment Object).
    #c2_flow(exp_name = "T0_Reading", plate_n = "1", time = str(time.strftime("%H_%M_%S", time.localtime())), local_path=flow_title, fname = fname, exp = exp)

    # Incubate for 12 hours
    # print("Incubating plate for 12 hours")
    # time.sleep(43200)

    # Run the T12 Workflow on the Registered WEI Experiment with the payload specified above to read the plate after the 12 hour wait
    # flow_info = exp.run_job(T12_wf_path.resolve(), payload=payload, simulate=False)
    
    # Pinging the status of the T0 Workflow sent to the WEI Experiment
    # flow_status = exp.query_job(flow_info["job_id"])
    # #Periodically checking the status every 3 seconds of the T0 Workflow until it is finished
    # while(flow_status["status"] != "finished" and flow_status["status"] != "failure"):
    #     flow_status = exp.query_job(flow_info["job_id"])
    #     time.sleep(3)
    
    # Receiving the Results of the now completed T0 Workflow, Creating a Path of the Run Directory, and printing the Run Information
    # run_info = flow_status["result"]
    # run_info["run_dir"] = Path(run_info["run_dir"])
    # print(run_info)

    # # Accessing the T12 Reading results file path from the Hidex 
    # hidex_file_path = run_info["hist"]["run Hidex"]["action_msg"]
    # # Formatting the File Path from Windows to be compatible with Linux file directory settings and creating a Path
    # hidex_file_path = hidex_file_path.replace('\\', '/')
    # hidex_file_path = hidex_file_path.replace("C:/", "/C/")
    # flow_title = Path(hidex_file_path) #Path(run_info["hist"]["run_assay"]["step_response"])
    # # Accessing the File Name
    # fname = flow_title.name
    # # Accessing the File Path
    # flow_title = flow_title.parents[0]
    
    #Uploading the Hidex Data to the Globus client and portal. The arguments in the function are the strings of the experiment name (exp_name), plate number (plate_n), time uploaded (time), the flow_title (local_path), and file name (fname), and the WEI Experiment Object).
    #Experiment name is T12_Reading to easily distinguish from the initial T0 Results in a Globus Portal Search
    #c2_flow(exp_name = "T12_Reading", plate_n = "1", time = str(time.strftime("%H_%M_%S", time.localtime())), local_path=flow_title, fname = fname, exp = exp)


if __name__ == "__main__":
    main()
