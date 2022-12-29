from hermes import *
from apollo import * 

# DUMMY & INPUY_NUM: each from 1 to 10 

eda_dict = { 
    'de_morgan': 1, 
    'trials': 100,
    'input_num': 2, 
    'dummy': 1, 
    'drawing': 1, 
    'print': 0, 
    'diff_bal': 1, 
    'output_num': 10, 
    'up': 1, 
    'low': 0, 
    'mode': 'automatic'
}

for dummy in range(1, 5):
    for input_num in range(1, 5):
        # print(f'dummy = {dummy}, input_')
        eda_dict['dummy'] = dummy
        eda_dict['input_num'] = input_num
        eda_wrapper(eda_dict)