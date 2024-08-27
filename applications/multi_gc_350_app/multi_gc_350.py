#!/usr/bin/env python3

import time
from datetime import datetime, timedelta
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
        "shaker_speed": 20,  # an integer value setting the shaker speed of the Liconic Incubator
        "tip_box_position": "1",  # string of an integer 1-8 that identifies the position of the tip box when it is being refilled
    }

    # parse the run details csv and add the information to the payload
    run_details = parse_run_details_csv(run_details_csv_path)

    num_assay_plates = run_details[0]
    incubation_hours = run_details[1]
    payload["treatment_stock_column"] = run_details[2]
    payload["culture_stock_column"] = run_details[2]
    payload["culture_dilution_column"] = run_details[4]
    payload["media_stock_start_column"] = run_details[5]
    payload["treatment_dilution_half"] = run_details[6]


    # Run Workcell Setup Workflow (preheat the hidex to 37C)
    exp.start_run(
        workflow_file=wc_setup_wf_path,
        payload=payload,
        blocking=False,
        simulate=False,
    )

    # Loop to create assay plates
    for i in range(num_assay_plates):
        payload["current_assay_plate_num"] = i + 1
        payload["plate_id"] = str(i + 1)

        print(f"Current assay plate number: {payload['current_assay_plate_num']}")
        print(f"Plate ID: {payload['plate_id']}")

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


        # # refill the tips (software step) before every two assay plates
        if (i % 2) == 0:
            exp.start_run(
                workflow_file=refill_tips_wf_path,
                payload=payload,
                # blocking=True,
                simulate=False,
            )

        # # # Run the T0 workflow
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

        # # TODO: fix the globus stuff
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

    incubation_seconds = incubation_hours * 3600
    time.sleep(incubation_seconds - (2160 * (num_assay_plates -1)))  # 12 hours = 43200 seconds, T0 half takes ~36 min to run (2160 seconds)
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=incubation_seconds - (2160 * (num_assay_plates -1)))

    # TESTING
    print(f"incubation_hours: {incubation_hours}")
    print(f"incubation_seconds: {incubation_seconds}")
    print(f"starting sleep at {start_time.strftime('%I:%M:%S %p')}")
    print(f"ending sleep at {end_time.strftime('%I:%M:%S %p')}")
    print(f"Now sleeping for {incubation_seconds - (2160 * (num_assay_plates -1))} seconds")


    # Loop to read assay plates
    for i in range(num_assay_plates):

        payload["current_assay_plate_num"] = i + 1
        payload["plate_id"] = str(i + 1)    # growth test will fail because of this !!!!!!

        # Testing
        print(f"Current assay plate number: {payload['current_assay_plate_num']}")
        print(f"Plate ID: {payload['plate_id']}")

        # Run the T12 workflow
        run_info = exp.start_run(
            workflow_file=T12_wf_path,
            payload=payload,
            blocking=True,
            simulate=False,
        )

        # Collect and save the Hidex data from the T0 reading
        output_dir = Path.home() / "runs" / run_info.experiment_id
        output_dir.mkdir(parents=True, exist_ok=True)
        datapoint_id = run_info.get_datapoint_id_by_label("T12_result")
        exp.save_datapoint_value(datapoint_id, output_dir / f"T12_result_{payload['plate_id']}.xlsx")

        # Wait to run the next assay plate (Assay plate took ~36 min to create and T0 read but T12 reading only takes ~9min )
        if i != num_assay_plates - 1:
            time.sleep(1620)
            start_time = datetime.now()
            end_time = start_time + timedelta(seconds=1620)
            print(f"starting sleep at {start_time.strftime('%I:%M:%S %p')}")
            print(f"ending sleep at {end_time.strftime('%I:%M:%S %p')}")
            print("Now sleeping for 1620 seconds")
            pass


        # TODO: Globus things again


if __name__ == "__main__":
    main()