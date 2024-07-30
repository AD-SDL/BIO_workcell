import csv
import os 
import pandas as pd


def parse_run_details_csv(run_detials_csv_path: str): 
    """parse_run_details_csv

    Parses the run details csv file and returns formatted run details

    Args:
        run_details_csv_path (str): Path to the run details csv

    Returns: 
        
    """
    print("HELPER METHOD CALLED")
    num_assay_plates = None
    treatment_stock_columm = []
    culture_stock_colum = []
    culture_dilution_colum = []
    media_stock_column = []
    treatment_dilution_column = []


    

    try: 
        if os.path.isfile(run_detials_csv_path): 
            df = pd.read_csv(run_detials_csv_path)
            print(df)

            

    
    except Exception as e: 
        raise e




"""Total Runs,12,,,,,,,,,,,,
Incubation Hours,12,,,,,,,,,,,,
Assay Plate Number,1,2,3,4,5,6,7,8,9,10,11,12,
Treatment Stock Column,1,2,3,4,5,6,7,8,9,10,11,12,
Culture Stock Column,12,11,10,9,8,7,6,5,4,3,2,1,
Media Stock Start Column,1,3,5,7,9,11,1,3,5,7,9,11,
Treatment Dilution Half,1,2,1,2,1,2,1,2,1,2,1,2,
"""