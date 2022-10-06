from pickle import FALSE
import yaml
import boolean
import random

algebra = boolean.BooleanAlgebra()

def read_config():
    with open('config.yaml') as conf:
        read_dict = yaml.load(conf, Loader=yaml.FullLoader)
    return read_dict

config_dict = read_config()
symbols_pool = ['a','b','c','d','e']

def main_loop():
    # This outer loop controls the number of trials
    for _ in range(config_dict['trials']):
        simply_input = generate_input()
        dumbly_input = add_dummy(simply_input)

# This function generates the most simplified input
def generate_input():
    symbols = symbols_pool[:config_dict['input_num']]

        #randomly negating the valid inputs in this layer
    for i in range(len(symbols)):
        rand_i = random.randint(0,1)
        if rand_i:
            symbols[i] = f"~{symbols[i]}"
    
    #randomly connecting the valid inputs in this layer
    for i in range(1,len(symbols)):
        rand_i = random.randint(0,1)
        if rand_i:
            symbols[i] = f"&{symbols[i]}"
        else: 
            symbols[i] = f"|{symbols[i]}"

    #put them all up into a valid base expression!
    qwq = ""
    for i in range(0, len(symbols)):
        qwq += symbols[i]

    return qwq

#This function generates the dummy-added inputs
def add_dummy(simple):
    symbols = symbols_pool[config_dict['input_num']:config_dict['dummy']+ config_dict['input_num']]
    for i in range(len(symbols)):
        rand_i = random.randint(0,3)
        # Annihilator
        if rand_i == 0:
            rand_j = random.randint(0,1)
            if rand_j:
                simple += f"|({symbols[i]}&{algebra.FALSE})"
            else:
                simple += f"&({symbols[i]}|{algebra.TRUE})"
        # Complementation
        if rand_i == 1:
            rand_j = random.randint(0,1)
            if rand_j:
                simple += f"|({symbols[i]}&~{symbols[i]})"
            else:
                simple += f"&({symbols[i]}|~{symbols[i]})"
        # Absorption
        if rand_i == 2:
            rand_j = random.randint(0,1)
            if rand_j:
                simple += f"&({simple}|{symbols[i]})"
            else:
                simple += f"|({simple}&{symbols[i]})"
        # Elimination
        if rand_i == 3:
            rand_j = random.randint(0,1)
            if rand_j:
                simple = f"{simple}&{symbols[i]}|{simple}&~{symbols[i]}"
            else:
                simple = f"({simple}|{symbols[i]})&({simple}&~{symbols[i]})"
    print(simple)
    return simple

main_loop()

