



def package_hso(
    create_hso_method,
    payload,
    temp_file_path,
):
    """package_hso

    Description: Calls method to create hso then reads contents into string and counts num lines

    Args:
        payload (_type_): _description_
        temp_file_path (_type_): _description_

    Returns:
        hso_contents: (str) contents of new hso file produced
        hso_num_lines: (int) number of lines in new hso file produced
    """

    try:
        # generate hso file at temp file path
        create_hso_method(payload=payload, temp_file_path=temp_file_path)

    except Exception as error_msg:
        # TODO: how to handle this?
        print("Could not create hso at specified temp file path")
        raise error_msg


    return temp_file_path


