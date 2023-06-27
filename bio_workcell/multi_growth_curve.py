#!/usr/bin/env python3

import logging
from argparse import ArgumentParser
import time
from tools.c2_flow import c2_flow
from pathlib import Path
from workflows.growth_curve.hso_functions import package_hso
from workflows.growth_curve import solo_step1, solo_step2, solo_step3
from workflows.growth_curve import solo_multi_step1, solo_multi_step2, solo_multi_step3

from rpl_wei import Experiment

#from rpl_wei.wei_workcell_base import WEI

EXPERIMENT_ITERATIONS = 1
INCUBATION_TIME_HOURS = 0.1
INCUBATION_TIME_MINUTES = INCUBATION_TIME_HOURS *  60
INCUBATION_TIME_SECONDS = INCUBATION_TIME_MINUTES * 60
HIDEX_IDLE_THRESHOLD_SECONDS = 3600

COMPLETE_HUDSON_SETUP_FILE_PATH = '/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/complete_hudson_setup.yaml'
STREAMLINED_HUDSON_SETUP_FILE_PATH = '/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/streamlined_hudson_setup.yaml'
SETUP_GROWTH_MEDIA_FILE_PATH = '/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/setup_growth_media.yaml'

CREATE_PLATE_T0_FILE_PATH = '/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/create_plate_T0.yaml'
READ_PLATE_T12_FILE_PATH = '/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/read_plate_T12.yaml'

DISPOSE_BOX_PLATE_FILE_PATH = '/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/dispose_box_plate.yaml'
DISPOSE_GROWTH_MEDIA_FILE_PATH = '/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/dispose_growth_media.yaml'

HIDEX_OPEN_CLOSE_FILE_PATH = '/home/rpl/workspace/BIO_workcell/bio_workcell/workflows/growth_curve/open_close_hidex.yaml'

exp = Experiment('127.0.0.1', '8000', 'Growth_Curve')
exp.register_exp() 
exp.events.log_local_compute("package_hso")

def main(): 
    iterations = 0
    removals = 0
    incubation_start_times = []
    #The experiment will run until all of the plates are used (indicated by iterations < EXPERIMENT_ITERATIONS) and there are no more plates in the incubator (indicated by len(incubation_start_times) != 0)
    while(iterations < EXPERIMENT_ITERATIONS or len(incubation_start_times) != 0):
        #Debug Log
        print("Starting Experiment ", iterations, ": Started Loop")
        #Check to see if there are any more plates to run, indicated by EXPERIMENT_ITERATIONS
        if(iterations < EXPERIMENT_ITERATIONS):
            #Set up the experiment based on the number of iterations passed.
            setup(iterations)
            #Calculate the ID of the plate needed for incubation based on the number of iterations that have passed
            liconic_id = iterations + 1
            #Run the experiment from the Hudson Solo step to the incubation step at a specified Liconic ID
            T0_Reading(liconic_id)
            #Add the time of the incubation start to the array of 96 well plates that are currently in the incubator
            incubation_start_times.append(round(time.time()))
            #Since an iteration has now passed (the plate is in the incubator), increase the index of incubation iterations
            iterations = iterations + 1
            #Debug Log
            print("Completed Iterations: ", iterations, " ... Start Times: " , incubation_start_times)
            #Based on the total number of completed incubation iterations, determine what needs to be disposed of from the experimental setup.
            if(iterations % 2 == 0):
                dispose(iterations)
        #Check to see if delta current time and the time at which the well plate currently incubating longest exceeds the incubation time.
        if(round(time.time()) - incubation_start_times[0] > INCUBATION_TIME_SECONDS):
            #Debug Log
            print("Finishing Up Experiment ", removals, ": Ending Loop")
            #Calcuate the ID of the 96 well plate needed for removal from the incubator based on the number of plates that have already been removed.
            liconic_id = removals + 1
            #Complete the experiment starting from the removal of the 96 well plate at the specified incubation ID and ending at a Hidex T12 Reading.
            T12_Reading(liconic_id)
            #Remove the incubation start time of the plate that was just read from the array to update the new longest incubating well plate
            incubation_start_times.pop(0)
            #Increase the total number of removals that have now occurred.
            removals = removals + 1


def dispose(completed_iterations):
    #Set the default disposal index of the serial dilution plate to Stack 2.
    disposal_index = "Stack2"
    #To identify the LidNest location of where certain serial dilution plates must be held, divide the completed iterations by 2
    stack_type = completed_iterations/2
    #For the first two serial dilution plates, define the disposal index as LidNest 1 for the first serial dilution plate and LidNest 2 for the second serial dilution plate
    if(stack_type <= 2):
        disposal_index = "LidNest" + str(int(stack_type))
    #For the fourth serial dilution plate, define the disposal index as LidNest 3.
    #We are not defining the disposal index as LidNest 3 for the third serial dilution plate because there will already be a growth media plate on LidNest 3. This growth media plate will be removed in the subsequent setup function
    if(stack_type == 4):
        disposal_index = "LidNest3"
    #Add the disposal index to the payload
    payload={
        'disposal_location':  disposal_index,    
        }
    #Run the despose Yaml File with the dedicated disposal location
    run_WEI(DISPOSE_BOX_PLATE_FILE_PATH, payload, False)
    if(stack_type % 3 == 0):
    #If the Stack Type is a multiple of 3 (6 complete iterations of the Hudson experiment have occurred), dispose of the growth media deep well plate
        run_WEI(DISPOSE_GROWTH_MEDIA_FILE_PATH, None, False)

def setup(iteration_number):
    #If currently on an even number of iterations, add a tip box, serial dilution plate, and 96 well plate to the experiment.
    if(iteration_number % 2 == 0):
        #Identify the Tip Box Position Index, so it can be refilled on the Hudson Client
        complete_payload={
                'tip_box_position': 3,
            }
        #Run the Yaml file that outlines the setup procedure for the tip box, serial dilution plate, and 96 well plate.
        run_WEI(COMPLETE_HUDSON_SETUP_FILE_PATH, complete_payload, False)
        #If currently on a number of iterations that is a factor of 6, add a growth media plate to the experiment as well
        if(iteration_number % 6 == 0):
            #Specify the LidNest index of the growth well media plate that will be added to the setup (This equation assumes that there are only two growth media plates on LidNest 2 and LidNest 3 respectively for a total of 12 runs)
            LidNest_index = 2 + iteration_number/6
            #Convert the index to a readable string
            plateCrane_readable_index = "LidNest" + str(int(LidNest_index))
            #Add the LidNest Index to the payload
            payload={
                'lidnest_index':  plateCrane_readable_index,
            }
            #Run the Yaml file that outlines the setup procedure for the growth media plate
            run_WEI(SETUP_GROWTH_MEDIA_FILE_PATH, payload, False)
    #If currently on an even number of iterations, add a 96 well plate to the experiment.
    else: 
        #Run the Yaml file that outlines the setup procedure for ONLY the 96 well plate
        run_WEI(STREAMLINED_HUDSON_SETUP_FILE_PATH, None, False)
        
def refreshHidex():
    run_WEI(HIDEX_OPEN_CLOSE_FILE_PATH, None, False)

def T0_Reading(liconic_plate_id):
    plate_id = '' + str(int(liconic_plate_id))
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
    hso_1, hso_1_lines, hso_1_basename = package_hso(solo_multi_step1.generate_hso_file, payload, "/home/rpl/wei_temp/solo_temp1.hso") 
    hso_2, hso_2_lines, hso_2_basename = package_hso(solo_multi_step2.generate_hso_file, payload, "/home/rpl/wei_temp/solo_temp2.hso")  
    hso_3, hso_3_lines, hso_3_basename = package_hso(solo_multi_step3.generate_hso_file, payload, "/home/rpl/wei_temp/solo_temp3.hso")  

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
    run_WEI(CREATE_PLATE_T0_FILE_PATH, payload, True)


def T12_Reading(liconic_plate_id):
    plate_id = '' + str(int(liconic_plate_id))

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
    hso_1, hso_1_lines, hso_1_basename = package_hso(solo_multi_step1.generate_hso_file, payload, "/home/rpl/wei_temp/solo_temp1.hso") 
    hso_2, hso_2_lines, hso_2_basename = package_hso(solo_multi_step2.generate_hso_file, payload, "/home/rpl/wei_temp/solo_temp2.hso")  
    hso_3, hso_3_lines, hso_3_basename = package_hso(solo_multi_step3.generate_hso_file, payload, "/home/rpl/wei_temp/solo_temp3.hso")  

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
    run_WEI(READ_PLATE_T12_FILE_PATH, payload, True)

def run_WEI(file_location, payload_class, Hidex_Used):
    flow_info = exp.run_job(Path(file_location).resolve(), payload=payload_class, simulate=False)

    flow_status = exp.query_job(flow_info["job_id"])
    while(flow_status["status"] != "finished" and flow_status["status"] != "failure"):
        flow_status = exp.query_job(flow_info["job_id"])
        time.sleep(3)

    run_info = flow_status["result"]
    run_info["run_dir"] = Path(run_info["run_dir"])

    # if Hidex_Used:
    #     print(run_info)
    #     hidex_file_path = run_info["hist"]["run Hidex"]["action_msg"]
    #     hidex_file_path = hidex_file_path.replace('\\', '/')
    #     hidex_file_path = hidex_file_path.replace("C:/", "/C/")
    #     flow_title = Path(hidex_file_path) #Path(run_info["hist"]["run_assay"]["step_response"])
    #     fname = flow_title.name
    #     flow_title = flow_title.parents[0]

    #     c2_flow("hidex_test", str(fname.split('.')[0]), hidex_file_path, flow_title, fname, exp)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3



# Previous Functions/Workflows

# def two():
#     iterations = 0
#     removals = 0
#     incubation_start_times = []

#     hidex_refresh_time = round(time.time())
#     EXPERIMENT_ITERATIONS = 2
#     while(iterations < EXPERIMENT_ITERATIONS or len(incubation_start_times) == 0):
#         if(iterations < EXPERIMENT_ITERATIONS):
#             setup(iterations)
#             liconic_id = iterations + 1
#             T0_Reading(liconic_id)
#             incubation_start_times.append(round(time.time()))
#             iterations = iterations + 1
#             if(iterations % 2 == 0):
#                 dispose()
#             #hidex_refresh_time = round(time.time())
#         if(round(time.time()) - incubation_start_times[0] > INCUBATION_TIME_SECONDS):
#             liconic_id = removals + 1
#             T12_Reading(liconic_id)
#             incubation_start_times.pop(0)
#             removals = removals + 1
#             #hidex_refresh_time = round(time.time())
#         #if(round(time.time()) - hidex_refresh_time < (HIDEX_IDLE_THRESHOLD_SECONDS - 20*60)):
#             #refreshHidex()

# def six():
#     iterations = 0
#     removals = 0
#     incubation_start_times = []

#     EXPERIMENT_ITERATIONS = 6
#     hidex_refresh_time = round(time.time())
#     EXPERIMENT_ITERATIONS = 2
#     while(iterations < EXPERIMENT_ITERATIONS or len(incubation_start_times) == 0):
#         if(iterations < EXPERIMENT_ITERATIONS):
#             setup(iterations)
#             liconic_id = iterations + 1
#             T0_Reading(liconic_id)
#             incubation_start_times.append(round(time.time()))
#             iterations = iterations + 1
#             if(iterations % 2 == 0):
#                 dispose()
#             #hidex_refresh_time = round(time.time())
#         if(round(time.time()) - incubation_start_times[0] > INCUBATION_TIME_SECONDS):
#             liconic_id = removals + 1
#             T12_Reading(liconic_id)
#             incubation_start_times.pop(0)
#             removals = removals + 1
#             #hidex_refresh_time = round(time.time())
#         #if(round(time.time()) - hidex_refresh_time < (HIDEX_IDLE_THRESHOLD_SECONDS - 20*60)):
#             #refreshHidex()

# def twelve():
#     iterations = 0
#     removals = 0
#     incubation_start_times = []

#     while(iterations < EXPERIMENT_ITERATIONS or len(incubation_start_times) == 0):
#         if(iterations < EXPERIMENT_ITERATIONS):
#             setup(iterations)
#             liconic_id = iterations + 1
#             T0_Reading(liconic_id)
#             incubation_start_times.append(round(time.time()))
#             iterations = iterations + 1
#             if(iterations % 2 == 0):
#                 dispose(iterations)
#             #hidex_refresh_time = round(time.time())
#         if(round(time.time()) - incubation_start_times[0] > INCUBATION_TIME_SECONDS):
#             liconic_id = removals + 1
#             T12_Reading(liconic_id)
#             incubation_start_times.pop(0)
#             removals = removals + 1
#             #hidex_refresh_time = round(time.time())
#         #if(round(time.time()) - hidex_refresh_time < (HIDEX_IDLE_THRESHOLD_SECONDS - 20*60)):
#             #refreshHidex()

# def base():
#     iterations = 0
#     removals = 0
#     incubation_start_times = []
#     while(iterations < EXPERIMENT_ITERATIONS or len(incubation_start_times) == 0):
#         if(iterations < EXPERIMENT_ITERATIONS):   
#             T0_Reading()
#             incubation_start_times.append(round(time.time()))
#             iterations = iterations + 1
#         if(round(time.time()) - incubation_start_times[0] > INCUBATION_TIME_SECONDS):
#             T12_Reading()
#             incubation_start_times.pop(0)

