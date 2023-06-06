#!/usr/bin/env python3

import logging
from pathlib import Path
from argparse import ArgumentParser
import time
from rpl_wei.wei_workcell_base import WEI
#from .tools.c2_flow import c2_flow
from pathlib import Path
from multiprocessing import Process
from workflows.growth_curve.hso_functions import package_hso
from workflows.growth_curve import solo_step1, solo_step2, solo_step3

EXPERIMENT_ITERATIONS = 4
INCUBATION_TIME_HOURS = 12
INCUBATION_TIME_MINUTES = INCUBATION_TIME_HOURS *  60
INCUBATION_TIME_SECONDS = INCUBATION_TIME_MINUTES * 60
TARGETED_PROCESS_TIME_MINUTES = 60
TARGETED_PROCESS_TIME_SECONDS = TARGETED_PROCESS_TIME_MINUTES * 60

def transfer():
    wf_path = Path('/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/test_platecrane_wf.yaml')

    wei_client = WEI(wf_config = wf_path.resolve(), workcell_log_level=logging.ERROR, workflow_log_level=logging.ERROR)

    # #run Growth Create Plate
    run_info = wei_client.run_workflow(payload=None)
    print(run_info)
    # # store plate_n, payload, and time into a db
    # # publish flow
    # # loop here
    # ###################
    # #check if any plate on db has 12h
    # #create new payload
    # #run measure_plate
    # #publish again
    # #loop here

def seal():
    wf_path = Path('/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/test_sealer_wf.yaml')

    wei_client = WEI(wf_config = wf_path.resolve(), workcell_log_level=logging.ERROR, workflow_log_level=logging.ERROR)

    # #run Growth Create Plate
    run_info = wei_client.run_workflow(payload=None)
    print(run_info)
    # # store plate_n, payload, and time into a db
    # # publish flow
    # # loop here
    # ###################
    # #check if any plate on db has 12h
    # #create new payload
    # #run measure_plate
    # #publish again
    # #loop here

    print(run_info)
    
if __name__ == "__main__":
    # seal()
    # transfer()
    
    p1 = Process(target = seal)
    p1.start()
    p2 = Process(target = transfer)
    p2.start()
    p1.join()
    p2.join()

        
        
        
