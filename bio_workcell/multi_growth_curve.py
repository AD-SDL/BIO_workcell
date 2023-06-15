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

COMPLETE_HUDSON_SETUP_FILE_PATH = '/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/complete_hudson_setup.yaml'
STREAMLINED_HUDSON_SETUP_FILE_PATH = '/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/streamlined_hudson_setup.yaml'
SETUP_GROWTH_MEDIA_FILE_PATH = '/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/setup_growth_media.yaml'

CREATE_PLATE_T0_FILE_PATH = '/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/create_plate_T0.yaml'
READ_PLATE_T12_FILE_PATH = '/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/read_plate_T12.yaml'

DISPOSE_BOX_PLATE_FILE_PATH = '/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/dispose_box_plate.yaml'
DISPOSE_GROWTH_MEDIA_FILE_PATH = '/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/dispose_growth_media.yaml'

HIDEX_OPEN_CLOSE_FILE_PATH = '/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/open_close_hidex.yaml'

incubation_start_times = []
iterations = 0
removals = 0

def main():
    while(iterations < EXPERIMENT_ITERATIONS or len(incubation_start_times) == 0):
        if(iterations < EXPERIMENT_ITERATIONS):
            setup(iterations)
            liconic_id = iterations + 1
            T0_Reading(liconic_id)
            incubation_start_times.append(round(time.time))
            iterations = iterations + 1
            if(iterations % 2 == 0):
                dispose(iterations)
        if(round(time.time) - incubation_start_times[0] > INCUBATION_TIME_SECONDS):
            liconic_id = removals + 1
            T12_Reading(liconic_id)
            incubation_start_times.pop(0)
            removals = removals + 1


def two():
    hidex_refresh_time = round(time.time)
    EXPERIMENT_ITERATIONS = 2
    while(iterations < EXPERIMENT_ITERATIONS or len(incubation_start_times) == 0):
        if(iterations < EXPERIMENT_ITERATIONS):
            setup(iterations)
            liconic_id = iterations + 1
            T0_Reading(liconic_id)
            incubation_start_times.append(round(time.time))
            iterations = iterations + 1
            if(iterations % 2 == 0):
                dispose()
            #hidex_refresh_time = round(time.time)
        if(round(time.time) - incubation_start_times[0] > INCUBATION_TIME_SECONDS):
            liconic_id = removals + 1
            T12_Reading(liconic_id)
            incubation_start_times.pop(0)
            removals = removals + 1
            #hidex_refresh_time = round(time.time)
        #if(round(time.time) - hidex_refresh_time < (HIDEX_IDLE_THRESHOLD_SECONDS - 20*60)):
            #refreshHidex()

def six():
    EXPERIMENT_ITERATIONS = 6
    hidex_refresh_time = round(time.time)
    EXPERIMENT_ITERATIONS = 2
    while(iterations < EXPERIMENT_ITERATIONS or len(incubation_start_times) == 0):
        if(iterations < EXPERIMENT_ITERATIONS):
            setup(iterations)
            liconic_id = iterations + 1
            T0_Reading(liconic_id)
            incubation_start_times.append(round(time.time))
            iterations = iterations + 1
            if(iterations % 2 == 0):
                dispose()
            #hidex_refresh_time = round(time.time)
        if(round(time.time) - incubation_start_times[0] > INCUBATION_TIME_SECONDS):
            liconic_id = removals + 1
            T12_Reading(liconic_id)
            incubation_start_times.pop(0)
            removals = removals + 1
            #hidex_refresh_time = round(time.time)
        #if(round(time.time) - hidex_refresh_time < (HIDEX_IDLE_THRESHOLD_SECONDS - 20*60)):
            #refreshHidex()

def twelve():
    while(iterations < EXPERIMENT_ITERATIONS or len(incubation_start_times) == 0):
        if(iterations < EXPERIMENT_ITERATIONS):
            setup(iterations)
            liconic_id = iterations + 1
            T0_Reading(liconic_id)
            incubation_start_times.append(round(time.time))
            iterations = iterations + 1
            if(iterations % 2 == 0):
                dispose(iterations)
            #hidex_refresh_time = round(time.time)
        if(round(time.time) - incubation_start_times[0] > INCUBATION_TIME_SECONDS):
            liconic_id = removals + 1
            T12_Reading(liconic_id)
            incubation_start_times.pop(0)
            removals = removals + 1
            #hidex_refresh_time = round(time.time)
        #if(round(time.time) - hidex_refresh_time < (HIDEX_IDLE_THRESHOLD_SECONDS - 20*60)):
            #refreshHidex()
    
def dispose(iterations):
    disposal_index = "Stack2"
    stack_type = iterations/2
    if(stack_type <= 2):
        disposal_index = "LidNest", stack_type
    if(stack_type == 4):
        disposal_index = "LidNest", 3
    payload={
        'disposal_location':  disposal_index,    
        }
    run_WEI(DISPOSE_BOX_PLATE_FILE_PATH, payload)
    if(stack_type % 3 == 0):
        run_WEI(DISPOSE_GROWTH_MEDIA_FILE_PATH, None)

def setup(iterations):
    if(iterations % 2 == 0):
        run_WEI(COMPLETE_HUDSON_SETUP_FILE_PATH, None)
        if(iterations % 6 == 0):
            LidNest_index = 3 - iterations/6
            payload={
                'lidnest_index':  LidNest_index,    
            }
            run_WEI(SETUP_GROWTH_MEDIA_FILE_PATH, payload)
    else: 
        run_WEI(STREAMLINED_HUDSON_SETUP_FILE_PATH, None)

def base():
    while(iterations < EXPERIMENT_ITERATIONS or len(incubation_start_times) == 0):
        if(iterations < EXPERIMENT_ITERATIONS):   
            T0_Reading()
            incubation_start_times.append(round(time.time))
            iterations = iterations + 1
        if(round(time.time) - incubation_start_times[0] > INCUBATION_TIME_SECONDS):
            T12_Reading()
            incubation_start_times.pop(0)
        
def refreshHidex():
    run_WEI(HIDEX_OPEN_CLOSE_FILE_PATH, None)

def T0_Reading(liconic_plate_id):
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

    #run Growth Create Plate
    run_WEI(CREATE_PLATE_T0_FILE_PATH, payload)


def T12_Reading(liconic_plate_id):
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
    run_WEI(READ_PLATE_T12_FILE_PATH, payload)

    # # store plate_n, payload, and time into a db
    # # publish flow
    # # loop here
    # ###################
    # #check if any plate on db has 12h
    # #create new payload
    # #run measure_plate
    # #publish again
    # #loop here

def run_WEI(file_location, payload_class):
    wf_path = Path(file_location)
    wei_client = WEI(wf_config = wf_path.resolve(), workcell_log_level=logging.ERROR, workflow_log_level=logging.ERROR)
    run_info = wei_client.run_workflow(payload=payload_class)
    print(run_info)

if __name__ == "__main__":
    main()
