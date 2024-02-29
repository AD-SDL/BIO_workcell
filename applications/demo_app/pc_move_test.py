#!/usr/bin/env python3

from pathlib import Path
import time

# from wei.wei_workcell_base import WEI
from wei import Experiment

from tools.hudson_solo_auxillary.hso_functions import package_hso
from tools.hudson_solo_auxillary import solo_transfer1

# DEMO APP

def main():
   
    # * Point to relevant workflow (yaml) file 
    wf_path = Path(
        "/home/rpl/workspace/BIO_workcell/demo_app/workflows/pc_move_test.yaml"
    )
  
    # * Creates a WEI Experiment at port 8000 and registers the experiment with the title Substrate
    exp = Experiment("127.0.0.1", "8000", "Demo")
    exp.register_exp()

    # * Generate the initial payload values (will update below to include SOLO liquid handler details)
    payload = {
        "temp": 37.0, #a float value setting the temperature of the Liconic Incubator (in Celsius) 
        "humidity": 95.0, # a float value setting the humidity of the Liconic Incubator
        "shaker_speed": 30, #an integer value setting the shaker speed of the Liconic Incubator
        "stacker": 1, # an integer value specifying which stacker a well plate should be used in (Preferable to use "incubation_plate_id" : plate_id, where plate_id is an integer 1-88 - stacker and slot will be autocalculated)
        "slot": 2, # an integer value specifying which slot a well plate should be used in (Preferable to use "incubation_plate_id" : plate_id, where plate_id is an integer 1-88 - stacker and slot will be autocalculated)
        "tip_box_position": "3", # string of an integer 1-8 that identifies the position of the tip box when it is being refilled
    }

    # * Package all .hso instructions needed to run the Hudson SOLO liquid handler
    # NOTE: There are multiple .hso files because the SOLO can only handle files with >70 steps/file
    # exp.events.log_local_compute("package_hso")  # note current step for logging

    # hso_1, hso_1_lines, hso_1_basename = package_hso(
    #     solo_transfer1.generate_hso_file, payload, "/home/rpl/wei_temp/solo_temp1.hso"
    # )


    # # * Add the HSO Packages to the payload to send to the Hudson Solo
    # payload["hso_1"] = hso_1
    # payload["hso_1_lines"] = hso_1_lines
    # payload["hso_1_basename"] = hso_1_basename

    # * Run the substrate step 1 workflow
    flow_info = exp.start_run(wf_path.resolve(), payload=payload, simulate=False)

    # Receive the results of the now completed workflow, create a path to the run directory, and print the run information
    run_info = flow_info["result"]
    print(run_info)

if __name__ == "__main__":
    main()
