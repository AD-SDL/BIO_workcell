import os
import sys
import time
import argparse
from liquidhandling import SoloSoft
from liquidhandling import Reservoir_12col_Agilent_201256_100_BATSgroup, Plate_96_Corning_3635_ClearUVAssay, DeepBlock_96VWR_75870_792_sterile

 
def generate_hso_file(
        payload, 
        temp_file_path,
): 
    """generate_hso_file

    Description: 
        Generates SOLOSoft .hso file for step 2 of the growth curve workflow

        Step 2 of the growth curve protocol includes:
            - Serial dilution of treatment 

    Args:
        payload (dict): input variables from the wei workflow
        temp_file_path (str): file path to temporarily save hso file to 
    """
    
    # extract payload variables
    try: 
        current_assay_plate_num = payload['current_assay_plate_num']
        treatment_stock_column = payload['treatment_stock_column'][current_assay_plate_num - 1]
        culture_stock_column = payload['culture_stock_column'][current_assay_plate_num - 1]
        culture_dilution_column = payload['culture_dilution_column'][current_assay_plate_num - 1]
        media_stock_start_column = payload['media_stock_start_column'][current_assay_plate_num - 1]
        treatment_dilution_half = payload['treatment_dilution_half'][current_assay_plate_num - 1]
        tip_box_position = f"Position{payload['tip_box_position']}"
    except Exception as error_msg: 
        # TODO: how to handle this?
        raise error_msg
    
    # Other protocol variables
    blowoff_volume = 10
    num_mixes = 3
    media_z_shift = 0.5
    reservoir_z_shift = 0.5  # z shift for deep blocks (Deck Positions 3 and 5)
    flat_bottom_z_shift = 2  # Note: 1 is not high enough (tested)

    # Step 2 variables
    media_transfer_volume_s2 = (
        120  # two times = 240 uL (will add 240 ul stock for 1:2 dilution)
    )
    last_column_transfer_volume_s2 = (
        120  # two times = 240uL (to equal volume in 1:10 dilution wells)
    )
    serial_antibiotic_transfer_volume_s2 = 120  # transfers twice (240tr + 240 lb = 1:2 dil)
    serial_source_mixing_volume_s2 = 110
    serial_source_num_mixes_s2 = 5
    serial_destination_mixing_volume_s2 = 150

    
    """
    STEP 2: PERFORM SERIAL DILUTIONS ON TREATMENT -------------------------------------------------------------------------------
    """
    # * Initialize soloSoft (step 2)
    soloSoft = SoloSoft(
        filename=temp_file_path,
        plateList=[
            "TipBox.180uL.Axygen-EVF-180-R-S.bluebox",
            "Plate.96.Corning-3635.ClearUVAssay",
            "DeepBlock.96.VWR-75870-792.sterile",
            "DeepBlock.96.VWR-75870-792.sterile",
            "DeepBlock.96.VWR-75870-792.sterile",
            "DeepBlock.96.VWR-75870-792.sterile",
            "DeepBlock.96.VWR-75870-792.sterile",
            "Empty",
        ],
    )

    # * Fill colums 1-5 of generic 96 well plate with 216uL lb media in two steps (will use for both halves of plate)
    soloSoft.getTip(tip_box_position)  
    for i in range(
        (6 * (treatment_dilution_half - 1)) + 1, (6 * (treatment_dilution_half - 1)) + 6
    ):  # columns 1-5 or columns 7-11 (treatment_dil_half = 1 or 2)
        # draws from both lb media wells to prevent running out of media
        soloSoft.aspirate(  # 120 from first lb media well
            position="Position7",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                media_stock_start_column, media_transfer_volume_s2
            ),
            aspirate_shift=[0, 0, media_z_shift],
            # pre_aspirate=blowoff_volume,
        )
        soloSoft.dispense(
            position="Position3",
            dispense_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                i, media_transfer_volume_s2
            ),
            dispense_shift=[0, 0, reservoir_z_shift],
            # blowoff=blowoff_volume,
        )

        soloSoft.aspirate(  # 120 from second lb media well
            position="Position7",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                media_stock_start_column + 1, media_transfer_volume_s2
            ),
            aspirate_shift=[0, 0, media_z_shift],
            # pre_aspirate=blowoff_volume,
        )
        soloSoft.dispense(
            position="Position3",
            dispense_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                i, media_transfer_volume_s2
            ),
            dispense_shift=[0, 0, reservoir_z_shift],
            # blowoff=blowoff_volume,
        )

    # TODO: combine this with loop above
    # * Fill column 6 of a generic 96 well plate with 240uL lb media total in two steps
    for i in range(media_stock_start_column, media_stock_start_column + 2):
        soloSoft.aspirate(  # first lb media well
            position="Position7",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                i, last_column_transfer_volume_s2
            ),
            aspirate_shift=[0, 0, media_z_shift],
            # pre_aspirate=blowoff_volume,
        )
        soloSoft.dispense(
            position="Position3",
            dispense_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                (6 * (treatment_dilution_half - 1)) + 6, last_column_transfer_volume_s2
            ),
            dispense_shift=[0, 0, reservoir_z_shift],
            # blowoff=blowoff_volume,
        )

    # * Transfer treatment into first column of treatment dilution plate (will make 1:2 dilution)
    for i in range(2):
        soloSoft.aspirate(
            position="Position4",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                treatment_stock_column, serial_antibiotic_transfer_volume_s2
            ),
            pre_aspirate=blowoff_volume,
            mix_at_start=True,
            mix_cycles=serial_source_num_mixes_s2,
            mix_volume=serial_source_mixing_volume_s2,
            aspirate_shift=[0, 0, reservoir_z_shift],
            dispense_height=reservoir_z_shift,
        )
        soloSoft.dispense(
            position="Position3",
            dispense_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                (6 * (treatment_dilution_half - 1)) + 1, serial_antibiotic_transfer_volume_s2
            ),
            dispense_shift=[0, 0, reservoir_z_shift],
            blowoff=blowoff_volume,
            # mix_at_finish=True,
            # mix_cycles=num_mixes,
            # mix_volume=serial_destination_mixing_volume_s2,
            aspirate_height=reservoir_z_shift,
        )

    # * Serial dilution within Generic 96 well plate (Corning or Falcon) - mix 3 times before and after transfer
    for i in range(
        (6 * (treatment_dilution_half - 1)) + 1, (6 * (treatment_dilution_half - 1)) + 5
    ):  # don't serial dilute into the last column (control column)
        # if i == 4:  # switch tips half way through to reduce error   #TODO: Test if you need this
        #     soloSoft.getTip()
        for j in range(2): 
            soloSoft.aspirate(
                position="Position3",
                aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    i, serial_antibiotic_transfer_volume_s2
                ),
                aspirate_shift=[0, 0, reservoir_z_shift],
                pre_aspirate=blowoff_volume,
                mix_at_start=True,
                mix_cycles=num_mixes,
                mix_volume=serial_destination_mixing_volume_s2,
                dispense_height=reservoir_z_shift,
            )
            soloSoft.dispense(
                position="Position3",
                dispense_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    i + 1, serial_antibiotic_transfer_volume_s2
                ),
                dispense_shift=[0, 0, reservoir_z_shift],
                blowoff=blowoff_volume,
                mix_at_finish=True,
                mix_cycles=num_mixes,
                mix_volume=serial_destination_mixing_volume_s2,
                aspirate_height=reservoir_z_shift,
            )
    # no need to throw away excess volume from last column of serial dilution

    soloSoft.shuckTip()
    soloSoft.savePipeline()




