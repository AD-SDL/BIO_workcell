#!/usr/bin/env python3

from pathlib import Path

import wei

#from tools.gladier_flow.growth_curve_gladier_flow import c2_flow
from tools.helper_functions import parse_run_details_csv
from tools.hudson_solo_auxillary import solo_step1, solo_step2, solo_step3
from tools.hudson_solo_auxillary.hso_functions import package_hso


def main():
    # directory paths
    bio_workcell_path = Path(__file__).parent.parent.parent
    app_dir = bio_workcell_path / "applications" / "multi_gc_350_app"
    wf_dir = app_dir / "workflows"

    # workflow paths
    wc_setup_wf_path = wf_dir / "workcell_setup.yaml"
    refill_tips_wf_path = wf_dir / "refill_tips.yaml"
    T0_wf_path = wf_dir / "create_plate_T0.yaml"
    T12_wf_path = wf_dir / "read_plate_T12.yaml"

    # run details csv path # TODO: make this an argument you can pass in?
    # run_details_csv_path = app_dir / "run_details.csv"
    run_details_csv_path = app_dir / "run_details_mini.csv"  # TESTING

    # Creates a WEI Experiment at the 8000 port and registers the experiment
    exp = wei.ExperimentClient(
        server_host="localhost",
        server_port="8000",
        experiment_name="Multi_GC_350",
        description="Growth Curve assay producing multiple assay plates on BIO350 workcell",
    )

    num_assay_plates = None

    # Initial payload setup
    payload = {
        "temp": 37.0,  # a float value setting the temperature of the Liconic Incubator (in Celsius)
        "humidity": 95.0,  # a float value setting the humidity of the Liconic Incubator
        "shaker_speed": 30,  # an integer value setting the shaker speed of the Liconic Incubator
        "tip_box_position": "1",  # string of an integer 1-8 that identifies the position of the tip box when it is being refilled
    }

    # parse the run details csv and add the information to the payload
    run_details = parse_run_details_csv(run_details_csv_path)
    num_assay_plates = run_details[0]
    payload["treatment_stock_column"] = run_details[1]
    payload["culture_stock_column"] = run_details[2]
    payload["culture_dilution_column"] = run_details[3]
    payload["media_stock_start_column"] = run_details[4]
    payload["treatment_dilution_half"] = run_details[5]


    # Run Workcell Setup Workflow (preheat the hidex to 37C)
    exp.start_run(
        workflow_file=wc_setup_wf_path,
        payload=payload,
        blocking=False,
        simulate=False,
    )

    # Lopping to create assay plates
    for i in range(num_assay_plates):
        payload["current_assay_plate_num"] = i + 1
        payload["plate_id"] = str(i + 1)

        # exp.events.log_local_compute("package_hso")  # TODO: Do I need to do this? What is the correct line for this now?

        # Generate the temp hso files
        hso_1_path = package_hso(
            solo_step1.generate_hso_file,
            payload,
            "/home/rpl/wei_temp/solo_temp1.hso"
        )
        hso_2_path = package_hso(
            solo_step2.generate_hso_file,
            payload,
            "/home/rpl/wei_temp/solo_temp2.hso"
        )
        hso_3_path = package_hso(
            solo_step3.generate_hso_file,
            payload,
            "/home/rpl/wei_temp/solo_temp3.hso"
        )

        # # Save the temp hso file paths into the payload
        payload["hso_1_path"] = hso_1_path
        payload["hso_2_path"] = hso_2_path
        payload["hso_3_path"] = hso_3_path

        print(payload["hso_1_path"])


        # refill the tips (software step) before every two assay plates
        if (i % 2) == 0:
            exp.start_run(
                workflow_file=refill_tips_wf_path,
                payload=payload,
                # blocking=True,
                simulate=False,
            )

        # Run the T0 workflow
        run_info = exp.start_run(
            workflow_file=T0_wf_path,
            payload=payload,
            blocking=True,
            simulate=False,
        )

        # Collect and save the Hidex data from the T0 reading
        output_dir = Path.home() / "runs" / run_info.experiment_id
        output_dir.mkdir(parents=True, exist_ok=True)
        datapoint_id = run_info.get_datapoint_id_by_label("T0_result")
        exp.save_datapoint_value(datapoint_id, output_dir / f"T0_result_{payload['plate_id']}.xlsx")

        # # TODO: clean these up
        # flow_title = Path(output_file_path)
        # fname = flow_title.name

        #
        # THIS IS FROM AN OLD WORKING VERISON FOR REFERENCE
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

        # Uploading the Hidex Data to the Globus client and portal. The arguments in the function are the strings of the experiment name (exp_name), plate number (plate_n), time uploaded (time), the flow_title (local_path), and file name (fname), and the WEI Experiment Object).
        # c2_flow(
        #     exp_name="T0_Reading",
        #     plate_n="1",
        #     time=str(time.strftime("%H_%M_%S", time.localtime())),
        #     local_path=flow_title,
        #     fname=fname,
        #     exp=exp,
        # )

    # time.sleep(43200)  # 12 hours = 43200 seconds  # TODO: subtract time it took to make the plates

    # for i in range(num_assay_plates):

    #     payload["current_assay_plate_num"] = i + 1

    #     # Run the T12 Workflow
    #     run_info = exp.start_run(
    #         workflow_file=T12_wf_path,
    #         payload=payload,
    #         # blocking=True,
    #         simulate=False,
    #     )

    #     # TODO: collect the Hidex data from the run info and do something with it
    #     hidex_file_name = run_info["hist"]["run Hidex"]["action_msg"]
    #     output_dir = Path.home() / "runs" / run_info["experiment_id"]
    #     output_dir.mkdir(parents=True, exist_ok=True)
    #     exp.get_wf_result_file(run_id=run_info["run_id"], filename=hidex_file_name, output_filepath=output_dir / hidex_file_name)

    #     time.sleep(500)  # TODO: Determine difference in T0 and T12

    #     # Pinging the status of the T0 Workflow sent to the WEI Experiment every 3 seconds  # TODO: Do we need this???
    #     flow_status = exp.query_job(flow_info["job_id"])
    #     while flow_status["status"] != "finished" and flow_status["status"] != "failure":
    #         flow_status = exp.query_job(flow_info["job_id"])
    #         time.sleep(3)

    #     # TODO: AT THIS POINT: plate is just placed in incubator (timestamp)

    #     # Receiving the Results of the now completed T0 Workflow, Creating a Path of the Run Directory, and printing the Run Information
    #     run_info = flow_status["result"]
    #     run_info["run_dir"] = Path(run_info["run_dir"])
    #     print(run_info)

    #     # Accessing the T0 Reading results file path from the Hidex
    #     hidex_file_path = run_info["hist"]["run Hidex"]["action_msg"]

    #     # Formatting the File Path from Windows to be compatible with Linux file directory settings and creating a Path
    #     hidex_file_path = hidex_file_path.replace('\\', '/')
    #     hidex_file_path = hidex_file_path.replace("C:/", "/C/")
    #     flow_title = Path(hidex_file_path) #Path(run_info["hist"]["run_assay"]["step_response"])

    #     # Accessing the File Name
    #     fname = flow_title.name

    #     # Accessing the File Path
    #     flow_title = flow_title.parents[0]

    #     # TODO: Get globus things working again
    #     # #Uploading the Hidex Data to the Globus client and portal. The arguments in the function are the strings of the experiment name (exp_name), plate number (plate_n), time uploaded (time), the flow_title (local_path), and file name (fname), and the WEI Experiment Object).
    #     # c2_flow(exp_name = "T0_Reading", plate_n = "1", time = str(time.strftime("%H_%M_%S", time.localtime())), local_path=flow_title, fname = fname, exp = exp)

    #     # END PLATE CREATION LOOP

    # # Incubate for 12 hours
    # print("Incubating plate for 12 hours")
    # time.sleep(43200)    # TODO: Change this so we don't have to manually

    # # BEGIN READ PLATE T12 LOOP
    # for i in range(num_assay_plates):
    #     # Run the T12 Workflow on the Registered WEI Experiment with the payload specified above to read the plate after the 12 hour wait
    #     flow_info = exp.run_job(wf_path_2.resolve(), payload=payload, simulate=False)

    #     # Pinging the status of the T0 Workflow sent to the WEI Experiment
    #     flow_status = exp.query_job(flow_info["job_id"])
    #     #Periodically checking the status every 3 seconds of the T0 Workflow until it is finished
    #     while(flow_status["status"] != "finished" and flow_status["status"] != "failure"):
    #         flow_status = exp.query_job(flow_info["job_id"])
    #         time.sleep(3)

    #     # Receiving the Results of the now completed T0 Workflow, Creating a Path of the Run Directory, and printing the Run Information
    #     run_info = flow_status["result"]
    #     run_info["run_dir"] = Path(run_info["run_dir"])
    #     print(run_info)

    #     # Accessing the T12 Reading results file path from the Hidex
    #     hidex_file_path = run_info["hist"]["run Hidex"]["action_msg"]
    #     # Formatting the File Path from Windows to be compatible with Linux file directory settings and creating a Path
    #     hidex_file_path = hidex_file_path.replace('\\', '/')
    #     hidex_file_path = hidex_file_path.replace("C:/", "/C/")
    #     flow_title = Path(hidex_file_path) #Path(run_info["hist"]["run_assay"]["step_response"])
    #     # Accessing the File Name
    #     fname = flow_title.name
    #     # Accessing the File Path
    #     flow_title = flow_title.parents[0]

    #     #Uploading the Hidex Data to the Globus client and portal. The arguments in the function are the strings of the experiment name (exp_name), plate number (plate_n), time uploaded (time), the flow_title (local_path), and file name (fname), and the WEI Experiment Object).
    #     #Experiment name is T12_Reading to easily distinguish from the initial T0 Results in a Globus Portal Search
    #     c2_flow(exp_name = "T12_Reading", plate_n = "1", time = str(time.strftime("%H_%M_%S", time.localtime())), local_path=flow_title, fname = fname, exp = exp)


if __name__ == "__main__":
    main()