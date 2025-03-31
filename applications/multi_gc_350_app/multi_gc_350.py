#!/usr/bin/env python3

from datetime import datetime, timedelta
from pathlib import Path
import time

# import wei   # OLD VERSION
from wei import ExperimentClient
from wei.types.experiment_types import CampaignDesign, ExperimentDesign

#from tools.gladier_flow.growth_curve_gladier_flow import c2_flow
from tools.helper_functions import parse_run_details_csv
from tools.hudson_solo_auxillary import solo_step1, solo_step2, solo_step3
from tools.hudson_solo_auxillary.hso_functions import package_hso

"""
If you get an error saying 'no module wei',
you need to source the .venv.

use:
source .venv/bin/activate
"""


def main():
    # Directory paths
    bio_workcell_path = Path(__file__).parent.parent.parent
    app_dir = bio_workcell_path / "applications" / "multi_gc_350_app"
    wf_dir = app_dir / "workflows"

    # Workflow paths
    wc_setup_wf_path = wf_dir / "workcell_setup.yaml"
    refill_tips_wf_path = wf_dir / "refill_tips.yaml"
    T0_wf_path = wf_dir / "create_plate_T0.yaml"
    T12_wf_path = wf_dir / "read_plate_T12.yaml"

    # run details csv path # TODO: make this an argument you can pass in?
    # run_details_csv_path = app_dir / "run_details.csv"
    run_details_csv_path = app_dir / "run_details_mini.csv"  # TESTING

    # Creates a WEI Experiment at the 8000 port and registers the experiment
    experiment_design = ExperimentDesign(
        experiment_name="MULTI_GC_350",
        experiment_description="Experiment application for the growth curve experiment",
    )

    campaign = CampaignDesign(
        campaign_name="AMP_Campaign",
        campaign_description="Campaign to collect experiments related to the AMP LDRD",
    )
    # define the experiment client object that will communicate with the WEI server
    experiment_client = ExperimentClient(
        server_host="localhost",
        server_port="8000",
        experiment=experiment_design,
        campaign=campaign,
    )

    num_assay_plates = None

    # Initial payload setup
    payload = {
        "temp": 37.0,  # a float value setting the temperature of the Liconic Incubator (in Celsius)
        "humidity": 95.0,  # a float value setting the humidity of the Liconic Incubator
        "shaker_speed": 20,  # an integer value setting the shaker speed of the Liconic Incubator
        "tip_box_position": "1",  # string of an integer 1-8 that identifies the position of the tip box when it is being refilled
    }

    # Parse the run details csv and add the information to the payload
    run_details = parse_run_details_csv(run_details_csv_path)

    num_assay_plates = run_details[0]
    incubation_hours = run_details[1]
    payload["treatment_stock_column"] = run_details[2]
    payload["culture_stock_column"] = run_details[3]
    payload["culture_dilution_column"] = run_details[4]
    payload["media_stock_start_column"] = run_details[5]
    payload["treatment_dilution_half"] = run_details[6]

    # Run Workcell Setup Workflow (preheat the hidex to 37C)
    experiment_client.start_run(
        workflow=wc_setup_wf_path,
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

        # Save the temp hso file paths into the payload
        payload["hso_1_path"] = hso_1_path
        payload["hso_2_path"] = hso_2_path
        payload["hso_3_path"] = hso_3_path


        # Refill the tips (software step) before every two assay plates
        if (i % 2) == 0:
            experiment_client.start_run(
                workflow=refill_tips_wf_path,
                payload=payload,
                # blocking=True,
                simulate=False,
            )

        # Run the T0 workflow  # TODO: does this method of collecting files still work?
        run_info = experiment_client.start_run(
            workflow=T0_wf_path,
            payload=payload,
            blocking=True,
            simulate=False,
        )

        # Collect and save the Hidex data from the T0 reading
        output_dir = Path.home() / "runs" / run_info.experiment_id
        output_dir.mkdir(parents=True, exist_ok=True)
        datapoint_id = run_info.get_datapoint_id_by_label("T0_result")
        experiment_client.save_datapoint_value(datapoint_id, output_dir / f"T0_result_{payload['plate_id']}.xlsx")

    # Calculate total incubation time and sleep to allow for incubation
    incubation_seconds = incubation_hours * 3600
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=incubation_seconds - (2160 * (num_assay_plates -1)))

    # TESTING
    print(f"incubation_hours: {incubation_hours}")
    print(f"incubation_seconds: {incubation_seconds}")
    print(f"starting sleep at {start_time.strftime('%I:%M:%S %p')}")
    print(f"ending sleep at {end_time.strftime('%I:%M:%S %p')}")
    print(f"Now sleeping for {incubation_seconds - (2159 * (num_assay_plates -1))} seconds")

    # Sleep for the total incubation time
    time.sleep(incubation_seconds - (2160 * (num_assay_plates - 1)))  # T0 portion takes ~36 min to run (2160 seconds)

    # Loop to read assay plates
    for i in range(num_assay_plates):

        payload["current_assay_plate_num"] = i + 1
        payload["plate_id"] = str(i + 1)

        # Testing
        print(f"Current assay plate number: {payload['current_assay_plate_num']}")
        print(f"Plate ID: {payload['plate_id']}")

        # Run the T12 workflow
        run_info = experiment_client.start_run(
            workflow=T12_wf_path,
            payload=payload,
            blocking=True,
            simulate=False,
        )

        # Collect and save the Hidex data from the T0 reading
        output_dir = Path.home() / "runs" / run_info.experiment_id
        output_dir.mkdir(parents=True, exist_ok=True)
        datapoint_id = run_info.get_datapoint_id_by_label("T12_result")
        experiment_client.save_datapoint_value(datapoint_id, output_dir / f"T12_result_{payload['plate_id']}.xlsx")

        # Wait to run the next assay plate (Assay plate took ~36 min to create and T0 read but T12 reading only takes ~9min )
        if i != num_assay_plates - 1:

            # Print information about incubation time
            start_time = datetime.now()
            end_time = start_time + timedelta(seconds=1620)
            print(f"starting sleep at {start_time.strftime('%I:%M:%S %p')}")
            print(f"ending sleep at {end_time.strftime('%I:%M:%S %p')}")
            print("Now sleeping for 1620 seconds")

            # Sleep to incubate until next assay plate is ready
            time.sleep(1620)


if __name__ == "__main__":
    main()