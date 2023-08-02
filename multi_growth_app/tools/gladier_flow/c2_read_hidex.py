from gladier import GladierBaseTool, generate_flow_definition


def excel_to_csv(**data):
    """
    Extracts Raw OD(590) data from Hidex excel file into csv file

    :param str filename: filename of Hidex excel file to convert

    output: path of new csv file (str)

    """
    import os
    from pathlib import Path
    import pandas as pd
    import csv
    import re
    from io import StringIO


    filepath = data.get('proc_folder')
    filename = data.get('file_name')
    filename = os.path.join(filepath,filename)
    sheet_name = "Raw OD(590)"
    csv_filename = None
    if os.path.exists(filename):
        excel_basename = os.path.splitext(os.path.basename(filename))[0]
        csv_filename = excel_basename + ".csv" #"_RawOD.csv"
        csv_filepath = filename.replace(os.path.basename(filename), csv_filename)

    # convert Raw OD(590) excel sheet to new csv file
    excel_OD_data = pd.read_excel(filename, sheet_name=sheet_name, index_col=None)
    excel_OD_data.columns = excel_OD_data.iloc[7][:]
    excel_OD_data = excel_OD_data[8:]
    excel_OD_data.columns = ["Plate #", "Well", "Reading Hour", 'Result']
    for i in range(8, len(excel_OD_data)+8):
        excel_OD_data.loc[i, "Plate #"] = str(int(data.get('plate_n')))
        excel_OD_data.loc[i, "Reading Hour"] = str(int(data.get('run_hour')))
    excel_OD_data.to_csv(csv_filepath, encoding="utf-8", index=False)

    experiment_info_string = data.get('experiment_run_df')
    # lines = re.split(r'\s{2,}', experiment_info_string.strip())
    # columns = lines[0].split()
    # data_rows = [line.split() for line in lines[1:]]
    # experiment_info_df = pd.DataFrame(data_rows, columns=columns)

    experiment_info_df = pd.read_csv(StringIO(experiment_info_string), sep='\t')

    # csv_df = pd.concat([excel_OD_data, experiment_info_df], axis=1)
    experiment_info_df.to_csv(csv_filepath, encoding="utf-8", index=False)
    # excel_OD_data.to_csv(csv_filepath, encoding="utf-8", index=False)
    return csv_filepath



@generate_flow_definition
class C2_read_hidex(GladierBaseTool):
    funcx_functions = [excel_to_csv]
    required_input = ['funcx_endpoint_compute']
