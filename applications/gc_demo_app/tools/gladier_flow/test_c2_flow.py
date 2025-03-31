import time
from pathlib import Path

from growth_curve_gladier_flow import c2_flow

flow_title = Path("/home/rpl/runs/01J5XFA8GYKCB6M1EDT0MN10PG/T0_result_1.xlsx")
fname = flow_title.name
# THIS IS FROM AN OLD WORKING VERISON FOR REFERENCE
# Formatting the File Path from Windows to be compatible with Linux file directory settings and creating a Path

# Accessing the File Path
flow_title = flow_title.parents[0]
print("FILE PATH")
print(flow_title)

# Uploading the Hidex Data to the Globus client and portal. The arguments in the function are the strings of the experiment name (exp_name), plate number (plate_n), time uploaded (time), the flow_title (local_path), and file name (fname), and the WEI Experiment Object).
c2_flow(
    exp_name="T0_Reading",
    plate_n="1",
    time=str(time.strftime("%H_%M_%S", time.localtime())),
    local_path=flow_title,
    fname=fname,

)