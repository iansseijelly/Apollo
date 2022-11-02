# This is the actual runner called when running stuffs, with args

import os
import random
from functools import reduce

import schemdraw
import yaml
from schemdraw.parsing import logicparse

import boolean
import apollo

import argparse

def read_config():
    with open('config.yaml') as conf:
        read_dict = yaml.load(conf, Loader=yaml.FullLoader)
    return read_dict

config_dict = read_config()

# When Charon is run as a script, run the following
if __name__ == "__main__":

    arg_list = argparse.ArgumentParser()

    arg_list.add_argument("-t", "--trials", type=int, default=config_dict['trials'], help="trial steps")
    arg_list.add_argument("-i", "--input_num", type=int, default=config_dict['input_num'], help="number of inputs in the final answer")
    arg_list.add_argument("-d", "--dummy", type=int, default=config_dict['dummy'], help="number of dummy variables in the final output")
    args = vars(arg_list.parse_args())

    apollo.main_loop(args)