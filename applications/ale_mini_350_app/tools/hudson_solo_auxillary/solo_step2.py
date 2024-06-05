
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
        Generates SOLOSoft .hso file for step 2 of the substrates workflow

    Args:
        payload (dict): input variables from the wei workflow
        temp_file_path (str): file path to temporarily save hso file to 
    """
    
        # extract payload variables
    try: 
        # treatment = payload['treatment'] 
        substrates_start_column_2 = payload['substrates_start_column_2']
  
    except Exception as error_msg: 
        # TODO: how to handle this?
        raise error_msg


# * Other program variables
    media_z_shift = 0.5
    flat_bottom_z_shift = 2  # Note: 1 is not high enough (tested)

    # Step 1 variables
    substrates_transfer_volume = 15 # check the volume

    # * Initialize soloSoft (step 2)
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

    # * Inoculate column 1 of 96 well plate
    soloSoft.getTip("Position1")  
    # j = 1
 
    soloSoft.aspirate(
        position="Position3",
        aspirate_volumes=DeepBlock_96VWR_75870_792_sterile().setColumn(
            substrates_start_column_2, substrates_transfer_volume
        ),
        aspirate_shift=[0, 0, media_z_shift],
        )
    soloSoft.dispense(
        position="Position2",
        dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
            1, substrates_transfer_volume
        ),
        dispense_shift=[0, 0, flat_bottom_z_shift],
    )

    soloSoft.shuckTip()
    soloSoft.savePipeline()