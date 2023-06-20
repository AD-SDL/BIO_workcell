#!/usr/bin/env python3

import logging
from pathlib import Path
from argparse import ArgumentParser
from rpl_wei.wei_workcell_base import WEI
from tools.c2_flow import c2_flow
from pathlib import Path
from datetime import datetime
from workflows.growth_curve.hso_functions import package_hso
from workflows.growth_curve import solo_step1, solo_step2, solo_step3
import time

def main():

    time_intervals_seconds = []
    #time_intervals_seconds = [5, 10, 15, 20, 30, 60]

    hidex_path_1 = Path('/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/hidex_open_close.yaml')
    hidex_path_2 = Path('/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/hidex_open_close_two.yaml')

    wei_client = WEI(wf_config = hidex_path_1.resolve(), workcell_log_level=logging.ERROR, workflow_log_level=logging.ERROR)
    run_info = wei_client.run_workflow(payload=None)
    print("Time: ", round(time.time()))
    print(run_info)
    time.sleep(4500)
    wei_client = WEI(wf_config = hidex_path_2.resolve(), workcell_log_level=logging.ERROR, workflow_log_level=logging.ERROR)
    run_info = wei_client.run_workflow(payload=None)
    print(run_info)
    print("Time: ", round(time.time()))

    # # #run Growth Create Plate

    # for designated_time in time_intervals_seconds:
    #     time.sleep(designated_time)
    #     interval_hours = designated_time/3600
    #     run_info = wei_client.run_workflow(payload=None)
    #     print("Successful Run Information: ", "Wait Time (Seconds): ", designated_time, ", Wait Time (Hours): ", interval_hours)
    #     print(run_info)




    # test = run_info["hist"]["run Hidex"]["step_response"]
    # test = test.replace('\\', '/')
    # test = test.replace("C:/", "/C/")
    # flow_title = Path(test) #Path(run_info["hist"]["run_assay"]["step_response"])
    # fname = flow_title.name
    # flow_title = flow_title.parents[0]
    # c2_flow("hidex_test", str(fname.split('.')[0]), "test", flow_title, fname)

    # wait while incubating

    # # read plate
    # test = run_info["hist"]["run Hidex"]["step_response"]
    # test = test.replace('\\', '/')
    # test = test.replace("C:/", "/C/")
    # flow_title = Path(test) #Path(run_info["hist"]["run_assay"]["step_response"])
    # fname = flow_title.name
    # flow_title = flow_title.parents[0]
    # c2_flow("hidex_test", str(fname.split('.')[0]), "test", flow_title, fname)

    # un_workflow(payload=payload)
    #     print(run_info)
    # orkflow(payload=payload)
    #     print(run_info)
    # # store plate_n, payload, and time into a db
    # # publish flow
    # # loop here
    # ###################
    # #check if any plate on db has 12h
    # #create new payload
    # #run measure_plate
    # #publish again
    # #loop here
    
if __name__ == "__main__":
    main()
