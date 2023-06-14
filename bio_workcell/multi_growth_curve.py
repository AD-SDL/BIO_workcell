#!/usr/bin/env python3

import logging
from pathlib import Path
from argparse import ArgumentParser
import time
from rpl_wei.wei_workcell_base import WEI
from .tools.c2_flow import c2_flow
from pathlib import Path

from workflows.growth_curve.hso_functions import package_hso
from workflows.growth_curve import solo_step1, solo_step2, solo_step3

EXPERIMENT_ITERATIONS = 12
INCUBATION_TIME_HOURS = 12
INCUBATION_TIME_MINUTES = INCUBATION_TIME_HOURS *  60
INCUBATION_TIME_SECONDS = INCUBATION_TIME_MINUTES * 60
TARGETED_PROCESS_TIME_MINUTES = 60
TARGETED_PROCESS_TIME_SECONDS = TARGETED_PROCESS_TIME_MINUTES * 60
HIDEX_IDLE_THRESHOLD_SECONDS = 3600
times = []
iterations = 0
removals = 0

def main():
    six() 

def two():
    hidex_refresh_time = round(time.time)
    EXPERIMENT_ITERATIONS = 2
    while(iterations < EXPERIMENT_ITERATIONS or len(times) == 0):
        if(iterations < EXPERIMENT_ITERATIONS):
            if(iterations % 2 == 0):
                setup(True)
            else: 
                setup(False)  
            liconic_id = iterations + 1
            tZero(liconic_id)
            times.append(round(time.time))
            iterations = iterations + 1
            if(iterations % 2 == 0):
                dispose()
            #hidex_refresh_time = round(time.time)
        if(round(time.time) - times[0] > INCUBATION_TIME_SECONDS):
            liconic_id = removals + 1
            tOne(liconic_id)
            times.pop(0)
            removals = removals + 1
            #hidex_refresh_time = round(time.time)
        #if(round(time.time) - hidex_refresh_time < (HIDEX_IDLE_THRESHOLD_SECONDS - 20*60)):
            #refreshHidex()

def six():
    EXPERIMENT_ITERATIONS = 6
    hidex_refresh_time = round(time.time)
    EXPERIMENT_ITERATIONS = 2
    while(iterations < EXPERIMENT_ITERATIONS or len(times) == 0):
        if(iterations < EXPERIMENT_ITERATIONS):
            if(iterations % 2 == 0):
                setup(True)
            else: 
                setup(False)
            liconic_id = iterations + 1
            tZero(liconic_id)
            times.append(round(time.time))
            iterations = iterations + 1
            if(iterations % 2 == 0):
                dispose()
            #hidex_refresh_time = round(time.time)
        if(round(time.time) - times[0] > INCUBATION_TIME_SECONDS):
            liconic_id = removals + 1
            tOne(liconic_id)
            times.pop(0)
            removals = removals + 1
            #hidex_refresh_time = round(time.time)
        #if(round(time.time) - hidex_refresh_time < (HIDEX_IDLE_THRESHOLD_SECONDS - 20*60)):
            #refreshHidex()

def dispose():
    wf_path = Path('/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/dispose_box_plate.yaml')
    wei_client = WEI(wf_config = wf_path.resolve(), workcell_log_level=logging.ERROR, workflow_log_level=logging.ERROR)
    run_info = wei_client.run_workflow(payload=None)
    print(run_info)

def setup(tip_box_and_growth_media):
    if(tip_box_and_growth_media):
        wf_path = Path('/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/complete_hudson_setup.yaml') 
        wei_client = WEI(wf_config = wf_path.resolve(), workcell_log_level=logging.ERROR, workflow_log_level=logging.ERROR)
        run_info = wei_client.run_workflow(payload=None)
        print(run_info)

    else:
        wf_path = Path('/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/streamlined_hudson_setup.yaml') 
        wei_client = WEI(wf_config = wf_path.resolve(), workcell_log_level=logging.ERROR, workflow_log_level=logging.ERROR)
        run_info = wei_client.run_workflow(payload=None)
        print(run_info)

def base():
    while(iterations < EXPERIMENT_ITERATIONS or len(times) == 0):
        if(iterations < EXPERIMENT_ITERATIONS):   
            tZero()
            times.append(round(time.time))
            iterations = iterations + 1
        if(round(time.time) - times[0] > INCUBATION_TIME_SECONDS):
            tOne()
            times.pop(0)
        
def refreshHidex():
    wf_path = Path('/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/open_close_hidex.yaml') #Open_Close_Hidex File Path

    wei_client = WEI(wf_config = wf_path.resolve(), workcell_log_level=logging.ERROR, workflow_log_level=logging.ERROR)

    run_info = wei_client.run_workflow(payload=None)
    print(run_info)

def tZero(liconic_plate_id):
    wf_path = Path('/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/create_plate_T0.yaml') 

    wei_client = WEI(wf_config = wf_path.resolve(), workcell_log_level=logging.ERROR, workflow_log_level=logging.ERROR)
    plate_id = '', liconic_plate_id

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
        "incubation_plate_id" : plate_id,        
        }

    # from somewhere import create_hso? or directly the solo script
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
    run_info = wei_client.run_workflow(payload=payload)
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

def tOne(liconic_plate_id):
    wf_path = Path('/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/read_plate_T12.yaml')
    wei_client = WEI(wf_config = wf_path.resolve(), workcell_log_level=logging.ERROR, workflow_log_level=logging.ERROR)

    plate_id = '', liconic_plate_id

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
        "incubation_plate_id" : plate_id,
        }

    # from somewhere import create_hso? or directly the solo script
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
    run_info = wei_client.run_workflow(payload=payload)
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
if __name__ == "__main__":
    main()
