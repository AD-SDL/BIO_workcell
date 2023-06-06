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

soloIterations = 0
completedReadings = 0
incubations = 0
liconicStartTime = 0.0

def solodolo():
    wf_path = Path('/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/hudson_experiment_wf.yaml')

    wei_client = WEI(wf_config = wf_path.resolve(), workcell_log_level=logging.ERROR, workflow_log_level=logging.ERROR)

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

def setaside():
    wf_path = Path('/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/hudson_aside_wf.yaml')

    wei_client = WEI(wf_config = wf_path.resolve(), workcell_log_level=logging.ERROR, workflow_log_level=logging.ERROR)

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

def solosetup():
    wf_path = Path('/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/hudson_setup_wf.yaml')

    wei_client = WEI(wf_config = wf_path.resolve(), workcell_log_level=logging.ERROR, workflow_log_level=logging.ERROR)


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

def endprocess():
    wf_path = Path('/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/parallel_endprocess_wf.yaml')

    wei_client = WEI(wf_config = wf_path.resolve(), workcell_log_level=logging.ERROR, workflow_log_level=logging.ERROR)

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

def incubateprocesses():
    wf_path = Path('/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/parallel_incubateprocess_wf.yaml')

    wei_client = WEI(wf_config = wf_path.resolve(), workcell_log_level=logging.ERROR, workflow_log_level=logging.ERROR)

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

def incubatethenRead():
    incubateprocesses()
    endprocess()
    
if __name__ == "__main__":  
    while(soloIterations < EXPERIMENT_ITERATIONS or incubations < EXPERIMENT_ITERATIONS or completedReadings < EXPERIMENT_ITERATIONS):
        previousProcessTime = round(time.time)
        #Zero State -- Just setting up the Hudson Solo experiment, running the Hudson Solo, and finally setting the well plate aside
        if(soloIterations == 0 and  incubations == 0 and completedReadings == 0):
            solosetup()
            solodolo()
            setaside()
            soloIterations = soloIterations + 1
        #Every State After - Split it up into first Run With No Previous Incubation, Previous Incubation but Below Wait Time, and Previous Incubation and Above Wait Time
        else:
            if(soloIterations < EXPERIMENT_ITERATIONS):
                solosetup()
                if(liconicStartTime == 0.0):
                    p1 = Process(target = solodolo)
                    p1.start()
                    p2 = Process(target = incubateprocesses)
                    p2.start()
                    p1.join()
                    p2.join()
                    liconicStartTime = round(time.time())
                    incubations = incubations + 1
                elif(round(time.time) - liconicStartTime < INCUBATION_TIME_SECONDS):
                    p1 = Process(target = solodolo)
                    p1.start()
                    p2 = Process(target = incubateprocesses)
                    p2.start()
                    p1.join()
                    p2.join()
                    incubations = incubations + 1
                elif(round(time.time) - liconicStartTime >= INCUBATION_TIME_SECONDS): 
                    p1 = Process(target = solodolo)
                    p1.start()
                    p2 = Process(target = incubateprocesses)
                    p2.start()
                    p1.join()
                    p2.join()
                    incubations = incubations + 1
                    completedReadings = completedReadings + 1
                setaside()
                soloIterations = soloIterations + 1
            elif(incubations < EXPERIMENT_ITERATIONS):
                incubatethenRead()
                incubations = incubations + 1
                completedReadings = completedReadings + 1
            else:
                endprocess()
                completedReadings = completedReadings + 1
        time.sleep(TARGETED_PROCESS_TIME_SECONDS - round(time.time) + previousProcessTime)
            
'''
    ALP DEMIRTAS FIRST ITERATION - 6/5/2023 
    soloIterations = 0
    completedReadings = 0 
    incubations = 0
    liconicStartTime = 0.0
    solosetup()
    solodolo()
    for i in range (0, EXPERIMENT_ITERATIONS + INCUBATION_TIME_MINUTES/TARGETED_PROCESS_TIME_MINUTES):
        if(i < EXPERIMENT_ITERATIONS):
            ## There is a potential bottleneck here - does the entire hudson must run before it goes onto the next line or are they both called in parallel?
            solodolo() #Can write the specific iteration of each index in the arguments here and for the liconic
            incubateprocesses()
            if(i == 0):
                liconicStartTime = round(time.time())
        if(i < EXPERIMENT_ITERATIONS - 1):
            solosetup()
        if(round(time.time()) > INCUBATION_TIME_SECONDS + liconicStartTime):
            endprocess()
        time.sleep(TARGETED_PROCESS_TIME_SECONDS - round(time.time) + previousProcessTime)
        previousProcessTime = round(time.time)
    '''


        
        

        
        
        
