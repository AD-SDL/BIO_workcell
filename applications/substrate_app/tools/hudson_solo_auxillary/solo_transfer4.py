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

        Basic steps:
            - transfer 150uL from substrate stock plate column 7 into each 12 columns of a 96 well plate at SOLO position 4
            - transfer 150uL from substrate stock plate column 9 into each 12 columns of a 96 well plate at SOLO position 5

    Args:
        payload (dict): input variables from the wei workflow
        temp_file_path (str): file path to temporarily save hso file to 
    """
    
    # extract payload variables (a commented out example)
    # try: 
    #     # treatment = payload['treatment'] 
    #     # culture_column = payload['culture_column']
    #     # culture_dil_column = payload['culture_dil_column']
    #     # media_start_column = payload['media_start_column']
    #     # treatment_dil_half = payload['treatment_dil_half']
    # except Exception as error_msg: 
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
    SOLO STEP 4: TRANSFER SUBSTRATE STOCK INTO REPLICATE PLATES 6 AND 7  -----------------------------------------------------------------
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

    # * Sixth set of 12 substrate column transfers (Stock plate column 7 --> replicate plate in position 4)
    soloSoft.getTip("Position3")  
    for i in range(1, 13):  # repeat for all 12 columns of replicate plate
        soloSoft.aspirate(
            position="Position2",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                7, substrate_transfer_volume
            ),
            aspirate_shift=[0, 0, media_z_shift],
        )
        soloSoft.dispense(
            position="Position4",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i, substrate_transfer_volume
            ),
            dispense_shift=[0, 0, flat_bottom_z_shift],
        )
    
    # * Seventh set of 12 substrate column transfers (Stock plate column 9 --> replicate plate in position 5)
    soloSoft.getTip("Position3")  # NOTE: Previous tips will be shucked automatically as part of .getTip() command
    for i in range(1, 13):  # repeat for all 12 columns of replicate plate
        soloSoft.aspirate(
            position="Position2",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                9, substrate_transfer_volume
            ),
            aspirate_shift=[0, 0, media_z_shift],
        )
        soloSoft.dispense(
            position="Position5",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i, substrate_transfer_volume
            ),
            dispense_shift=[0, 0, flat_bottom_z_shift],
        )

    # * Dispense tips at end of protocol and process these instructions into a .hso file 
    soloSoft.shuckTip()
    soloSoft.savePipeline()
    