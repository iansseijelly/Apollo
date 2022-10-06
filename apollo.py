from ast import parse
from pickle import FALSE
import yaml
import boolean
import random
from functools import reduce

from schemdraw.parsing import logicparse

algebra = boolean.BooleanAlgebra()

def read_config():
    with open('config.yaml') as conf:
        read_dict = yaml.load(conf, Loader=yaml.FullLoader)
    return read_dict

config_dict = read_config()
symbols_pool = ['a','b','c','d','e','f','g','h']

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
    candidates = [rev_annihilator, rev_complementation, rev_absorption, rev_elimination]
    symbols = symbols_pool[config_dict['input_num']:config_dict['dummy']+ config_dict['input_num']]
    for i in range(len(symbols)):
        symbol = symbols[i]
        rand_i = random.randint(0,3)
        simple = candidates[rand_i](simple, symbol)
    return simple

# Annihilator
def rev_annihilator(simple, symbol):
    rand_j = random.randint(0,1)
    if rand_j:
        simple += f"|({symbol}&{algebra.FALSE})"
    else:
        simple += f"&({symbol}|{algebra.TRUE})"
    return simple

# Complementation
def rev_complementation(simple, symbol):
    rand_j = random.randint(0,1)
    if rand_j:
        simple += f"|({symbol}&~{symbol})"
    else:
        simple += f"&({symbol}|~{symbol})"
    return simple

# Absorption
def rev_absorption(simple, symbol):
    rand_j = random.randint(0,1)
    if rand_j:
        simple += f"&({simple}|{symbol})"
    else:
        simple += f"|({simple}&{symbol})"
    return simple

# Elimination
def rev_elimination(simple, symbol):
    rand_j = random.randint(0,1)
    if rand_j:
        simple = f"{simple}&{symbol}|{simple}&~{symbol}"
    else:
        simple = f"({simple}|{symbol})&({simple}|~{symbol})"
    return simple

def test_transform(input, symbol, func):
    output = func(input, symbol)
    qwq = algebra.parse(input).simplify()
    print(output)
    qaq = algebra.parse(output).simplify()
    if qwq == qaq:
        print("the two are equal!")
    else:
        print("NAH")
    print(qwq)
    print(qaq)

def de_morgan(dumb_input):
    for _ in range(config_dict['de_morgan']):
        parsed = algebra.parse(dumb_input)
        print(f'parsed is \n {parsed.pretty()}')
        lst = [boolean.NOT(i) for i in parsed.args]
        qwq = reduce(parsed.dual, lst)
        qwq = boolean.NOT(qwq)
        print(f'qwq is \n {qwq.pretty()}')
        return qwq.__str__()

def main_loop():
    # This outer loop controls the number of trials
    ret_set = set()
    for _ in range(config_dict['trials']):
        simply_input = generate_input()
        dumbly_input = add_dummy(simply_input)
        output = de_morgan(dumbly_input)
        print(f"dumb is :{dumbly_input}")
        print(f"output is :{output}")
        ret_set.add(output)
    ret_list = list(ret_set)
    # print(ret_list)
    # print(ret_list[0])
    # with logicparse(ret_list[0], outlabel='$f$') as d:
    #     d.save('circuit.svg')
    #     return ret_set
    return ret_list


main_loop()
# test_transform("a&b", "c", rev_elimination)

