from gladier import GladierBaseTool, generate_flow_definition

def gather_metadata(**data):

    from pathlib import Path
    import json
    import os
    import csv
    import re
    import scipy.stats as stats

    GENERAL_METADATA = {
    "creators": [{"creatorName": "BIO Team"}],
    "publicationYear": "2023", 
    "publisher": "Argonne National Lab",
    "resourceType": {
        "resourceType": "Dataset",
        "resourceTypeGeneral": "Dataset"
    },
    "subjects": [{"subject": "SDL"}],
    "exp_type": "Campaign2"

    }

    input_path = Path(data['proc_folder']).expanduser()
    datal = {}
    for file in os.listdir(input_path):
        if re.match(".*csv", file):
            if file.startswith("blank_adj"):
                with open(input_path / file) as f:
                    reader = csv.reader(f)
                    vals = []
                    for row in reader:
                        vals.append(row)
                    datal["csvdata"] = vals
            elif file.startswith("best_fit"):
                with open(input_path / file) as f:
                    reader = csv.reader(f)
                    vals = []
                    for row in reader:
                        vals.append(row)
                    datal["best_fit_line_data"] = vals
          
        elif re.match(".*contam.txt", file):
            with open(input_path / file) as f:
                datal["contam"] =  f.read()

    GENERAL_METADATA.update(datal)
    final_data = data["publishv2"]
    final_data['metadata'] = GENERAL_METADATA
    return final_data

@generate_flow_definition
class GatherMetaData(GladierBaseTool):
    funcx_functions = [gather_metadata]
    required_input = [
        'funcx_endpoint_compute'
    ]
