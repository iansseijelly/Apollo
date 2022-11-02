import os
import random
from functools import reduce

import yaml
import csv

from schemdraw.parsing import logicparse

import boolean
import hermes

import numpy as np
import pandas as pd
import copy

algebra = boolean.BooleanAlgebra()
trans_list = []

def read_config():
    with open('config.yaml') as conf:
        read_dict = yaml.load(conf, Loader=yaml.FullLoader)
    return read_dict

config_dict = read_config()
symbols_pool = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

# This function generates the most simplified input
def generate_input(args):
    symbols = symbols_pool[:args['input_num']]

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
def add_dummy(simple, args):
    candidates = [rev_annihilator, rev_complementation, rev_absorption, rev_elimination]
    symbols = symbols_pool[args['input_num']:args['dummy']+ args['input_num']]
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
    if config_dict['de_morgan']:
        parsed = algebra.parse(dumb_input)
        if isinstance(parsed,boolean.AND) or isinstance(parsed,boolean.OR):
            lst = [boolean.NOT(i) for i in parsed.args]
            qwq = reduce(parsed.dual, lst)
            qwq = boolean.NOT(qwq)
            dumb_input = qwq.__str__()
    return dumb_input

# Compute the complexity of your expression
def comp_complex(expr):
    parsed = algebra.parse(expr)
    complexity = 0
    if parsed is not None and not isinstance(parsed, boolean.Symbol):
        complexity += len(parsed.args) + sum([comp_complex(i.__str__()) for i in parsed.args])
    return complexity
    
def main_loop(args):
    initiate_trans()
    # This outer loop controls the number of trials
    ans_list = []
    ret_list = []
    for _ in range(args['trials']):
        simply_input = generate_input(args)
        # print(f"the simply_input is: {simply_input}")
        dumbly_input = add_dummy(simply_input, args)
        # print(f"the dumbly_input is: {dumbly_input}")
        output = de_morgan(dumbly_input)
        # print(f"output is :{output}")
        if output not in ret_list:
            ret_list.append(output)
            ans_list.append(simply_input)
    # print(ret_list)
    # print(ret_list[0])
    # internal_checker(ans_list, ret_list)

    # A list storing all output blobs
    blob_list = []
    complexity_list = []
    balanced_ret_list = []
    # instantiating the blobs
    for i in range(len(ret_list)):
        new_blob = Blob(ret_list[i], ans_list[i], comp_complex(ret_list[i]))
        blob_list.append(new_blob)
        complexity_list.append(new_blob.complexity)

    # difficulty balancing zzz happening here!
    iterations = min(config_dict['output_num'], len(ret_list))
    data = np.array(complexity_list)
    upper_limit = np.median(data) + 1.5 * np.std(data)
    lower_limit = np.median(data) + 0.5 * np.std(data)
    judge = lambda x: x <= upper_limit and x >= lower_limit
    for _ in range(iterations):
        # emulated do while for picking an appropraite blob
        rand_j = random.randint(0,len(blob_list)-1)
        blob = blob_list[rand_j]
        while(blob.complexity > upper_limit):
            rand_j = random.randint(0,len(blob_list)-1)
            blob = blob_list[rand_j]
        # blob_list.remove(blob)
        blob = randomzoomies(blob, judge, upper_limit)
        balanced_ret_list.append(blob)

    # write into a csv for profiling
    header = ['output', 'answer', 'complexity']
    with open('data.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for i in range(len(blob_list)):
            bloby = blob_list[i]
            data = [bloby.output, bloby.answer, bloby.complexity]
            writer.writerow(data)

    # print out the output
    if config_dict['print']:
        print(f'before balancing: ')
        for i in range(len(blob_list)):
            qwq = blob_list[i]
            print(f'the {i}th answer is: {qwq.answer}')
            print(f'the {i}th output is: {qwq.output}')
            print(f'the {i}th output is complexity is: {qwq.complexity}')
        print('----------------------------')
        print(f'after balancing: ')
        for i in range(len(balanced_ret_list)):
            qwq = balanced_ret_list[i]
            print(f'the {i}th answer is: {qwq.answer}')
            print(f'the {i}th output is: {qwq.output}')
            print(f'the {i}th output is complexity is: {qwq.complexity}')
    
    # draw out the output
    if config_dict['drawing']:
        # This will cleanup the gen folder before generating new svgs, be careful.
        dir = 'gen'
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))
        for i in range(len(balanced_ret_list)):
            expr = balanced_ret_list[i].output
            expr_sub = expr.replace("0", "FALSE")
            expr_sub = expr_sub.replace("1", "TRUE")
            with logicparse(expr_sub, gateH = 1.1, outlabel="output") as d:
                d.save(f'gen/circuit{i}.svg')

    return ret_list, ans_list

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

def initiate_trans():
    double_negationer = Transform('double_negation', lambda x: f'~(~{x})')
    negative_absorptioner = Transform('negative_absorption', lambda x: neg_abs(x))
    idempotencer = Transform('idempotence', lambda x: idempotence(x))
    identitier = Transform('identity', lambda x: identity(x))
    global trans_list
    trans_list = [double_negationer, negative_absorptioner, idempotencer, identitier]

def identity(expr):
    rand_j = random.randint(0,1)
    if rand_j:
        return f"{expr}&{algebra.TRUE}"
    else:
        return f"{expr}|{algebra.FALSE}"

def idempotence(expr):
    rand_j = random.randint(0,1)
    if rand_j:
        return f"{expr}&{expr}"
    else:
        return f"{expr}|{expr}"

def neg_abs(expr):
    parsed = algebra.parse(expr)
    # print(parsed.pretty())
    if isinstance(parsed, boolean.AND):
        x = parsed.args[0]
        y = parsed.args[1]
        if len(parsed.args) == 3:
            z = parsed.args[2]
            qwq = boolean.AND(x, boolean.OR(boolean.NOT(x), y), z)
        if len(parsed.args) > 3:
            z = parsed.args[2:]
            qwq = boolean.AND(x, boolean.OR(boolean.NOT(x), y), z)
        else:
            qwq = boolean.AND(x, boolean.OR(boolean.NOT(x), y))
        return qwq.__str__()
    if isinstance(parsed, boolean.OR):
        x = parsed.args[0]
        y = parsed.args[1]
        if len(parsed.args) == 3:
            z = parsed.args[2]
            qwq = boolean.OR(x, boolean.AND(boolean.NOT(x), y), z)
        if len(parsed.args) > 3:
            z = parsed.args[2:]
            qwq = boolean.OR(x, boolean.AND(boolean.NOT(x), y), z)
        else:
            qwq = boolean.OR(x, boolean.AND(boolean.NOT(x), y))
        return qwq.__str__()
    else:
        return expr

def randomzoomies(blob, judge, upper_limit):
    print(blob.output)
    while not judge(blob.complexity):
        blob_copy = copy.deepcopy(blob)
        blob.output = randooooom(blob.output)
        print(f'after randooom {blob.output}')
        blob.complexity = comp_complex(blob.output)
        if blob.complexity > upper_limit:
            blob = blob_copy
    return blob

# one iteration of random complication
def randooooom(expr):
    parsed = algebra.parse(expr)
    if isinstance(expr, boolean.Symbol) or isinstance(expr, boolean.NOT):
        return complicator_helper(expr)
    if parsed == algebra.TRUE or parsed == algebra.FALSE:
        return parsed.__str__() 
    else:
        rand_i = random.randint(0,1)
        if rand_i:
            return complicator_helper(expr)
        else:
            # print(f'the random_k part')
            # print(f'{parsed.pretty()}')
            if len(parsed.args) == 0:
                parsed = randooooom(parsed.__str__())
            else:
                rand_k = random.randint(0, len(parsed.args)-1)
                temp = list(parsed.args)
                temp[rand_k] = algebra.parse(randooooom(parsed.args[rand_k].__str__()))
                parsed.args = tuple(temp)
            return parsed.__str__()

def complicator_helper(expr):
    global trans_list
    rand_t = random.randint(0, len(trans_list) - 1)
    transformer = trans_list[rand_t]
    print(rand_t)
    print(f'complicator helper output: {transformer.trans_func(expr)}')
    return transformer.trans_func(expr)


class Blob:
    def __init__(self, output, answer, complexity):
        self.output = output
        self.answer = answer
        self.complexity = complexity

class Transform:
    def __init__(self, name, trans_func):
        self.name = name
        self.trans_func = trans_func
