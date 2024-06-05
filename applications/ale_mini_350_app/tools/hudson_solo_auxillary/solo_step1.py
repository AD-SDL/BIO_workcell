
"""
Generates SOLO hso files given command line inputs

Returns paths to newly generated .hso files
"""
import os
import sys
import time
import argparse
from liquidhandling import SoloSoft
from liquidhandling import Reservoir_12col_Agilent_201256_100_BATSgroup, Plate_96_Corning_3635_ClearUVAssay, DeepBlock_96VWR_75870_792_sterile


# SOLO PROTOCOL STEPS    
def generate_hso_file(
        payload, 
        temp_file_path,
): 
    """generate_hso_file

    Description: 
        Generates SOLOSoft .hso file for step 1 of the substrates workflow

    Args:
        payload (dict): input variables from the wei workflow
        temp_file_path (str): file path to temporarily save hso file to 
    """
    
        # extract payload variables
    try: 
        # treatment = payload['treatment'] 
        substrates_start_column_1 = payload['substrates_start_column_1']
  
    except Exception as error_msg: 
        # TODO: how to handle this?
        raise error_msg


# * Other program variables
    media_z_shift = 0.5
    flat_bottom_z_shift = 2  # Note: 1 is not high enough (tested)

    # Step 1 variables
    substrates_transfer_volume = 150

    # * Initialize soloSoft (step 1)
    soloSoft = SoloSoft(
        filename=temp_file_path,
        plateList=[
            "TipBox.180uL.Axygen-EVF-180-R-S.bluebox",
            "Plate.96.Corning-3635.ClearUVAssay",
            "DeepBlock.96.VWR-75870-792.sterile",
            "Empty",
            "Empty",
            "Empty",
            "Empty",
            "Empty",
        ],
    )

    # * Fill all columns of empty 96 well plate (corning 3383 or Falcon - ref 353916) with fresh substrates (12 channel in Position 1, media_start_column and media_start_column+1)
    soloSoft.getTip("Position1")  
    # j = 1
    for i in range(1, 13):  
        soloSoft.aspirate(
            position="Position3",
            aspirate_volumes=DeepBlock_96VWR_75870_792_sterile().setColumn(
                substrates_start_column_1, substrates_transfer_volume
            ),
            aspirate_shift=[0, 0, media_z_shift],
        )
        soloSoft.dispense(
            position="Position2",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i, substrates_transfer_volume
            ),
            dispense_shift=[0, 0, flat_bottom_z_shift],
        )

    soloSoft.shuckTip()
    soloSoft.savePipeline()