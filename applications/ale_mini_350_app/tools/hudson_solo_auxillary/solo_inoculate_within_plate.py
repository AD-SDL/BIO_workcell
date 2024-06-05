"""
# TODO: Check the position of the tip box


Generates SOLO hso files given command line inputs

Returns paths to newly generated .hso files
"""
import os
import sys
import time
import argparse
from liquidhandling import SoloSoft
from liquidhandling import Plate_96_Corning_3635_ClearUVAssay


# SOLO PROTOCOL STEPS    
def generate_hso_file(
        payload, 
        temp_file_path,
): 
    """generate_hso_file

    Description: 
        Generates SOLOSoft.hso file for substrate inoculations between columns within
        substrate plate

    Args:
        payload (dict): input variables from the wei workflow
        temp_file_path (str): file path to temporarily save hso file to 
    """
    

    
    try: 
        loop_num = payload['loop_num']

        
    except Exception as error_msg: 
        # TODO: how to handle this?
        raise error_msg

    # other program variables
    flat_bottom_z_shift = 2  # Note: 1 is not high enough (tested)
    inoculant_transfer_volume = 10  # to be confirmed
    tip_box_position = "Position1"

    # * Initialize soloSoft
    soloSoft = SoloSoft(
        filename=temp_file_path,
        plateList=[
            "TipBox.50uL.Axygen-EV-50-R-S.tealbox",  
            "Plate.96.Corning-3635.ClearUVAssay",
            "Empty",  
            "Empty",
            "Empty",
            "Empty",
            "Empty",
            "Empty",
        ],
    )

    # First transfer 
    soloSoft.getTip(tip_box_position)
    soloSoft.aspirate(
        position="Position2",
        aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
            loop_num, 
            inoculant_transfer_volume
        ),
        aspirate_shift=[0, 0, flat_bottom_z_shift],
    )
    soloSoft.dispense(
        position="Position2",
        dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
            loop_num + 1,                 
            inoculant_transfer_volume
        ),
        dispense_shift=[0, 0, flat_bottom_z_shift],
    )

    # shuck tip and save instructions to .hso file
    soloSoft.shuckTip()
    soloSoft.savePipeline()