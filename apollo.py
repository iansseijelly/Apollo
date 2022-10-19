import os
import random
from functools import reduce

import schemdraw
import yaml
from schemdraw.parsing import logicparse

import boolean

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
        simple = f"({simple})|({symbol}&~({symbol}))"
    else:
        simple = f"({simple})&({symbol}|~({symbol}))"
    return simple

# Absorption
def rev_absorption(simple, symbol):
    rand_j = random.randint(0,1)
    if rand_j:
        simple = f"({simple})&({simple}|{symbol})"
    else:
        simple = f"({simple})|({simple}&{symbol})"
    return simple

# Elimination
def rev_elimination(simple, symbol):
    rand_j = random.randint(0,1)
    if rand_j:
        simple = f"({simple}&{symbol})|({simple}&(~({symbol})))"
    else:
        simple = f"({simple}|{symbol})&({simple}|~({symbol}))"
    return simple

# A test method to make sure your transforms actually work
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
        lst = [boolean.NOT(i) for i in parsed.args]
        qwq = reduce(parsed.dual, lst)
        qwq = boolean.NOT(qwq)
        return qwq.__str__()

def comp_complex(expr):
    parsed = algebra.parse(expr)
    complexity = 0
    if parsed is not None and not isinstance(parsed, boolean.Symbol):
        complexity += len(parsed.args) + sum([comp_complex(i.__str__()) for i in parsed.args])
    return complexity
    
def main_loop():
    # This outer loop controls the number of trials
    ans_list = []
    ret_list = []
    for _ in range(config_dict['trials']):
        simply_input = generate_input()
        # print(f"the simply_input is: {simply_input}")
        dumbly_input = add_dummy(simply_input)
        # print(f"the dumbly_input is: {dumbly_input}")
        output = de_morgan(dumbly_input)
        # print(f"output is :{output}")
        if output not in ret_list:
            ret_list.append(output)
            ans_list.append(simply_input)
    # print(ret_list)
    # print(ret_list[0])
    internal_checker(ans_list, ret_list)

    # print out the output
    if config_dict['print']:
        for i in range(len(ret_list)):
            print(f'the {i}th answer is: {ans_list[i]}')
            print(f'the {i}th output is: {ret_list[i]}')
            qwq = comp_complex(ret_list[i])
            print(f'the {i}th output is complexity is: {qwq}')

    if config_dict['drawing']:
        # This will cleanup the gen folder before generating new svgs, be careful.
        dir = 'gen'
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))
        for i in range(len(ret_list)):
            expr = ret_list[i]
            expr_sub = expr.replace("0", "FALSE")
            expr_sub = expr_sub.replace("1", "TRUE")
            with logicparse(expr_sub, gateH = 1.1, outlabel="output") as d:
                d.save(f'gen/circuit{i}.svg')

    return ret_list

# Check if the simplified output is different from the actual input or not, requires manual checking 
def internal_checker(ans_list, ret_list):
    assert len(ans_list) == len(ret_list), f"their length doesn't match, with anslength {len(ans_list)}, retlength {len(ret_list)}"
    for i in range(len(ans_list)):
        output = ret_list[i]
        output_simplified = algebra.parse(output).simplify().__str__()
        output_simp_demorganized = de_morgan_checker(output_simplified)
        ans = ans_list[i]
        if ans != output_simplified and ans != output_simp_demorganized:
            print(f"caution! unmatching output {output} and answer {ans} (simplified to {output_simplified} & demorgan conjugate: {output_simp_demorganized})")

def de_morgan_checker(dumb_input):
    parsed = algebra.parse(dumb_input)
    if isinstance(parsed, boolean.NOT):
        parsed = parsed.demorgan()
    return parsed.__str__()
            

# A test function for drawing your favorite circuit
def draw(expr):
    qwq = algebra.parse(expr)
    qaq = qwq.simplify()
    print(qwq)
    print(qaq)
    print(qwq.pretty())
    print(qaq.pretty())
    expr_sub = expr.replace("0", "FALSE")
    expr_sub = expr_sub.replace("1", "TRUE")
    with logicparse(expr_sub, outlabel="$out$") as d:
        d.save('gen/test_circuit.svg')

main_loop()
# test_transform("a&b", "c", rev_elimination)
# comp_complex("~(a|~b)")
        
# qwq = algebra.parse("~((~(a&~b))|(~((a&~b)|c)))")
# print(qwq.simplify())