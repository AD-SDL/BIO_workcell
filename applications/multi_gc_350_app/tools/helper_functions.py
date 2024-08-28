import os


def parse_run_details_csv(run_details_csv_path: str):
    """parse_run_details_csv

    Parses the run details csv file and returns formatted run details

    Args:
        run_details_csv_path (str): Path to the run details csv

    Returns:

    """
    num_assay_plates = None
    incubation_hours= None
    treatment_stock_column = []
    culture_stock_column = []
    culture_dilution_column = []
    media_stock_start_column = []
    treatment_dilution_half = []

    try:
        num_assay_plates = None
        if os.path.isfile(run_details_csv_path):
            with open(run_details_csv_path, "r") as run_details:
                contents = run_details.readlines()
                for line in contents:
                    line = line.split(",")

                    for entry in line:
                        entry = entry.strip()

                    if line[0] == "Total Runs":
                        num_assay_plates = int(line[1])

                    if line[0] == "Incubation Hours":
                        incubation_hours = int(line[1])


                    if num_assay_plates:
                        if line[0] == "Treatment Stock Column":
                            treatment_stock_column = [int(x) for x in line[1:num_assay_plates+1]]
                        if line[0] == "Culture Stock Column":
                            culture_stock_column = [int(x) for x in line[1:num_assay_plates+1]]
                        if line[0] == "Culture Dilution Column":
                            culture_dilution_column = [int(x) for x in line[1:num_assay_plates+1]]
                        if line[0] == "Media Stock Start Column":
                            media_stock_start_column = [int(x) for x in line[1:num_assay_plates+1]]
                        if line[0] == "Treatment Dilution Half":
                            treatment_dilution_half = [int(x) for x in line[1:num_assay_plates+1]]

    except Exception as e:
        raise e

    return (
        num_assay_plates,
        incubation_hours,
        treatment_stock_column,
        culture_stock_column,
        culture_dilution_column,
        media_stock_start_column,
        treatment_dilution_half,
    )


