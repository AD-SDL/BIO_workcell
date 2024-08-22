from gladier import GladierBaseTool, generate_flow_definition

def c2_best_fit(**data):
    import matplotlib.pyplot as plt
    import os
    import pandas as pd
    import scipy.stats as stats
    """

    Description: Received a blank adjusted data frame and produces the line of best fit for 6 wells

    Parameters: 
        blank_adj_df: blank adjusted data in data frame format
        data_filename: file name of the original data csv file without extension (not file path)
        plot_directory_path: path to the directory where all created graphs should be stored 

    Returns: 
        best_fit_path: the file path of the excel document with the best fit line slopes and intercepts
    
    """
    plot_directory_path = data.get("proc_folder")
    csv_file = os.path.join(plot_directory_path, data.get('csv_file'))
    ba_csv_file =  os.path.join(plot_directory_path, "blank_adj_" + data.get('csv_file'))
    data_filename = data.get('csv_file').split('.')[0]
#    blank_adj_df, data_filename, plot_directory_path

    blank_adj_df = pd.read_csv(ba_csv_file)

    best_fit_df = pd.DataFrame(columns=["Rows", "Best Fit Slope", "Best Fit Intercept"])
    for i in range(0,16):
        x_concentration = []
        y_results = []
        for j in range(1,7):
            if j == 0:
                x_concentration.append(0)
            else:
                x_concentration.append(0.5**j)
            data_frame_index = int(j + i*6) - 1
            cell_reading = float(blank_adj_df.loc[data_frame_index, "Result"])
            y_results.append(cell_reading)
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_concentration, y_results)
        print("Slope: ", slope)
        print("Intercept: ", intercept)
        print("X: ", x_concentration)
        print("Y: ", y_results)
        row_line = ''
        reading_type = int((i - i % 2) / 2)
        row_character = chr(65 + reading_type)
        if i % 2 == 0:
            row_line = row_character + "1 - " + row_character + "6"
        else:
            row_line = row_character + "7 - " + row_character + "12"
            
        new_row_data = {
            "Rows": str(row_line), 
            "Best Fit Slope": str(slope),
            "Best Fit Intercept": str(intercept)
        }

        new_row_df = pd.DataFrame(new_row_data, index=pd.RangeIndex(start=0, stop=1))   
        best_fit_df = pd.concat([best_fit_df, new_row_df], ignore_index=True)

    best_fit_df.to_csv( data.get("proc_folder") + "/best_fit_" + data.get('csv_file'), encoding="utf-8", index=False)

    return data.get("proc_folder") + "/best_fit_" + data.get('csv_file')


@generate_flow_definition
class C2_best_fit(GladierBaseTool):
    funcx_functions = [c2_best_fit]
    required_input = ['funcx_endpoint_compute']
