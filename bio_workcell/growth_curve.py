#!/usr/bin/env python3

from pathlib import Path
#from rpl_wei.wei_workcell_base import WEI
from tools.c2_flow import c2_flow
from pathlib import Path
from workflows.growth_curve.hso_functions import package_hso
from workflows.growth_curve import solo_step1, solo_step2, solo_step3
from rpl_wei import Experiment
import time

def main():
    wf_path_1 = Path('/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/create_plate_T0.yaml')
    wf_path_2 = Path('/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/read_plate_T12.yaml')
    exp = Experiment('127.0.0.1', '8000', 'Growth_Curve')
    exp.register_exp() 
    payload={
        'temp': 37.0, 
        'humidity': 95.0,
        'shaker_speed': 30,
        "stacker": 1, 
        "slot": 1,
        "treatment": "col1", # string of treatment name. Ex. "col1", "col2"
        "culture_column": 1,  # int of cell culture column. Ex. 1, 2, 3, etc.
        "culture_dil_column": 1, # int of dilution column for 1:10 culture dilutions. Ex. 1, 2, 3, etc.
        "media_start_column": 1,  # int of column to draw media from (requires 2 columns, 1 means columns 1 and 2) Ex. 1, 3, 5, etc.
        "treatment_dil_half": 1,  #  int of which plate half to use for treatment serial dilutions. Options are 1 or 2. 
        "tip_box_position" : 3,
        }

    # from somewhere import create_hso? or directly the solo script
    exp.events.log_local_compute("package_hso")
    hso_1, hso_1_lines, hso_1_basename = package_hso(solo_step1.generate_hso_file, payload, "/home/rpl/wei_temp/solo_temp1.hso") 
    hso_2, hso_2_lines, hso_2_basename = package_hso(solo_step2.generate_hso_file, payload, "/home/rpl/wei_temp/solo_temp2.hso")  
    hso_3, hso_3_lines, hso_3_basename = package_hso(solo_step3.generate_hso_file, payload, "/home/rpl/wei_temp/solo_temp3.hso")  

    # update payload with solo hso details
    payload['hso_1'] = hso_1
    payload['hso_1_lines'] = hso_1_lines
    payload['hso_1_basename'] = hso_1_basename

    payload['hso_2'] = hso_2
    payload['hso_2_lines'] = hso_2_lines
    payload['hso_2_basename'] = hso_2_basename

    payload['hso_3'] = hso_3
    payload['hso_3_lines'] = hso_3_lines
    payload['hso_3_basename'] = hso_3_basename
    
    # #run Growth Create Plate
    flow_info = exp.run_job(wf_path_1.resolve(), payload=payload, simulate=False)

    flow_status = exp.query_job(flow_info["job_id"])
    while(flow_status["status"] != "finished" and flow_status["status"] != "failure"):
        flow_status = exp.query_job(flow_info["job_id"])
        time.sleep(3)

    run_info = flow_status["result"]
    run_info["run_dir"] = Path(run_info["run_dir"])

    print(run_info)
    hidex_file_path = run_info["hist"]["run Hidex"]["action_msg"]
    hidex_file_path = hidex_file_path.replace('\\', '/')
    hidex_file_path = hidex_file_path.replace("C:/", "/C/")
    flow_title = Path(hidex_file_path) #Path(run_info["hist"]["run_assay"]["step_response"])
    fname = flow_title.name
    flow_title = flow_title.parents[0]
  
    c2_flow("hidex_test", str(fname.split('.')[0]), hidex_file_path, flow_title, fname, exp)
    #wait while incubating
    time.sleep(43200)

    # read plate
    flow_info = exp.run_job(wf_path_2.resolve(), payload=payload, simulate=False)

    flow_status = exp.query_job(flow_info["job_id"])
    while(flow_status["status"] != "finished" and flow_status["status"] != "failure"):
        flow_status = exp.query_job(flow_info["job_id"])
        time.sleep(3)

    run_info = flow_status["result"]
    run_info["run_dir"] = Path(run_info["run_dir"])
    hidex_file_path = run_info["hist"]["run Hidex"]["action_msg"]
    hidex_file_path = hidex_file_path.replace('\\', '/')
    hidex_file_path = hidex_file_path.replace("C:/", "/C/")
    flow_title = Path(hidex_file_path) #Path(run_info["hist"]["run_assay"]["step_response"])
    fname = flow_title.name
    flow_title = flow_title.parents[0]
  
    c2_flow("hidex_test", str(fname.split('.')[0]), hidex_file_path, flow_title, fname, exp)
    
if __name__ == "__main__":
    main()
