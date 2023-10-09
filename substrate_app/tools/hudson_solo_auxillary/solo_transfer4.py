"""
Generates SOLO .hso instruction file for fourth set of steps for substrate transfer experiment

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
        Generates SOLOSoft .hso file for step 4 of the substrate transfer workflow

        Step 4 of the substrate transfer workflow includes:
            - transfer 150uL from substrate stock plate column 10 into each 12 columns of a 96 well plate at SOLO position 6
            - transfer 150uL from substrate stock plate column 11 into each 12 columns of a 96 well plate at SOLO position 7

    Args:
        payload (dict): input variables from the wei workflow
        temp_file_path (str): file path to temporarily save hso file to 
    """
    
    # extract payload variables 
    # try: 
    #     # treatment = payload['treatment'] 
    #     # culture_column = payload['culture_column']
    #     # culture_dil_column = payload['culture_dil_column']
    #     # media_start_column = payload['media_start_column']
    #     # treatment_dil_half = payload['treatment_dil_half']
    # except Exception as error_msg: 
    #     # TODO: how to handle this?
    #     raise error_msg


# * Other program variables
    # general SOLO variables
    blowoff_volume = 10
    num_mixes = 3
    media_z_shift = 0.5
    reservoir_z_shift = 0.5  # z shift for deep blocks (Deck Positions 3 and 5)
    flat_bottom_z_shift = 2  # Note: 1 is not high enough (tested)

    # protocol specific variables
    substrate_transfer_volume = 150

    """
    SOLO STEP 1: TRANSFER FIRST SUBSTRATE STOCK INTO 3 REPLICATE PLATES  -----------------------------------------------------------------
    """
    # * Initialize soloSoft deck layout 
    soloSoft = SoloSoft(
        filename=temp_file_path,
        plateList=[
            "Empty",
            "DeepBlock.96.VWR-75870-792.sterile",       # substrate stock plate
            "TipBox.180uL.Axygen-EVF-180-R-S.bluebox",  # 180 uL tip box
            "Plate.96.Corning-3635.ClearUVAssay",       # substrate replicate plate
            "Plate.96.Corning-3635.ClearUVAssay",       # substrate replicate plate
            "Plate.96.Corning-3635.ClearUVAssay",       # substrate replicate plate
            "Plate.96.Corning-3635.ClearUVAssay",       # substrate replicate plate
            "Empty",       
        ],
    )

    # * Eighth set of 12 substrate column transfers (Stock plate column 10 --> replicate plate in position 6)
    soloSoft.getTip("Position3")  
    for i in range(1, 13):  # repeat for all 12 columns of replicate plate
        soloSoft.aspirate(
            position="Position2",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                10, substrate_transfer_volume
            ),
            aspirate_shift=[0, 0, media_z_shift],
        )
        soloSoft.dispense(
            position="Position6",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i, substrate_transfer_volume
            ),
            dispense_shift=[0, 0, flat_bottom_z_shift],
        )
    
    # * Ninth set of 12 substrate column transfers (Stock plate column 11 --> replicate plate in position 7)
    soloSoft.getTip("Position3")  # NOTE: Previous tips will be shucked automatically as part of .getTip() command
    for i in range(1, 13):  # repeat for all 12 columns of replicate plate
        soloSoft.aspirate(
            position="Position2",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                11, substrate_transfer_volume
            ),
            aspirate_shift=[0, 0, media_z_shift],
        )
        soloSoft.dispense(
            position="Position7",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i, substrate_transfer_volume
            ),
            dispense_shift=[0, 0, flat_bottom_z_shift],
        )

    # * Dispense tips at end of protocol and process these instructions into a .hso file 
    soloSoft.shuckTip()
    soloSoft.savePipeline()