import copy
import csv
import os
import random
from functools import reduce

import numpy as np
import pandas as pd
import schemdraw
import yaml
import traceback
# import schemdraw.elements as elm
# import schemdraw.logic.logic as lg
from schemdraw.parsing import logicparse

import boolean
# import hermes

EDA = True # change to False if not doing EDA 

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

    # randomly negating the valid inputs in this layer
    for i in range(len(symbols)):
        rand_i = random.randint(0,1)
        if rand_i:
            symbols[i] = f"~{symbols[i]}"
    
    # randomly connecting the valid inputs in this layer
    for i in range(1,len(symbols)):
        rand_i = random.randint(0,1)
        if rand_i:
            symbols[i] = f"&{symbols[i]}"
        else: 
            symbols[i] = f"|{symbols[i]}"

    # put them all up into a valid base expression!
    return "".join(symbols)

# This function generates the dummy-added inputs
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
    # qwq = boolean.DualBase.simplify(qwq)
    print(output)
    qaq = algebra.parse(output).simplify()
    # qaq = boolean.DualBase.simplify(qaq)
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
    
def main_loop(args, output_file=''):
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
    iterations = min(int(config_dict['output_num'] * 1.5), len(ret_list))
    data = np.array(complexity_list)
    up = config_dict['up']
    low = config_dict['low']
    upper_limit = np.median(data) + up * np.std(data)
    lower_limit = np.median(data) + low * np.std(data)
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

    # invoking the internal checker here
    new_list = []
    for i in range(len(balanced_ret_list)):
        bal_blob = balanced_ret_list[i]
        if internal_checker(bal_blob.output, bal_blob.answer):
            new_list.append(bal_blob)
    balanced_ret_list = new_list

    # write into a csv for profiling
    header = ['output', 'answer', 'complexity']
    if not output_file:
        output_file = 'data.csv'
    with open(output_file, 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for i in range(len(blob_list)):
            bloby = blob_list[i]
            data = [bloby.output, bloby.answer, bloby.complexity]
            writer.writerow(data)
    
    # draw out the output
    if config_dict['drawing']:
        # This will cleanup the gen folder before generating new svgs, be careful.
        dir = 'gen'
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))
        confirmed_balanced_ret_list = []
        for i in range(len(balanced_ret_list)):
            expr = balanced_ret_list[i].output
            if netlist(expr, i):
                confirmed_balanced_ret_list.append(balanced_ret_list[i])

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
        for i in range(len(confirmed_balanced_ret_list)):
            qwq = balanced_ret_list[i]
            print(f'the {i}th answer is: {qwq.answer}')
            print(f'the {i}th output is: {qwq.output}')
            print(f'the {i}th output is complexity is: {qwq.complexity}')
    print(confirmed_balanced_ret_list[0])
    return confirmed_balanced_ret_list

# Check if the simplified output is different from the actual input or not, requires manual checking 
def internal_checker(output, answer):
    output = output
    output_simplified = algebra.parse(output).simplify().__str__()
    # print('-------------************-------------')
    # print(f'TYPE = {type(output_simplified)}')
    # print('-------------************-------------')
    # output_simplified = str(boolean.DualBase.simplify(output_simplified))
    # .simplify().__str__()
    output_simp_demorganized = de_morgan_checker(output_simplified)
    ans = answer
    if ans != output_simplified and ans != output_simp_demorganized:
        print(f"caution! unmatching output {output} and answer {ans} (simplified to {output_simplified} & demorgan conjugate: {output_simp_demorganized})")
        return False
    return True

def de_morgan_checker(dumb_input):
    parsed = algebra.parse(dumb_input)
    if isinstance(parsed, boolean.NOT):
        parsed = parsed.demorgan()
    return parsed.__str__()

def initiate_trans():
    double_negationer = Transform('double_negation', lambda x: f'~(~({x}))' if len(x) > 1 else f'~(~{x})')
    negative_absorptioner = Transform('negative_absorption', lambda x: neg_abs(x))
    idempotencer = Transform('idempotence', lambda x: idempotence(x))
    identitier = Transform('identity', lambda x: identity(x))
    global trans_list
    trans_list = [negative_absorptioner, idempotencer, identitier]
    # trans_list = [negative_absorptioner]

# some more transitions here

def identity(expr):
    rand_j = random.randint(0,1)
    if rand_j:
        return f"({expr})&({algebra.TRUE})"
    else:
        return f"({expr})|({algebra.FALSE})"

def idempotence(expr):
    rand_j = random.randint(0,1)
    if rand_j:
        return f"({expr})&({expr})"
    else:
        return f"({expr})|({expr})"

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
    while not judge(blob.complexity):
        blob_copy = copy.deepcopy(blob)
        blob.output = randooooom(blob.output)
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
            # print("let's do it here")
            return complicator_helper(expr)
        else:
            # print("going down the stack")
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
    return transformer.trans_func(expr)

def netlist(expr, i):
    if config_dict["mode"] == "automatic":
        # print("bingo")

        expr = algebra.parse(expr).__str__()
        # expr = draw_preprocessing(expr)
        try:
            expr_sub = expr.replace("0", "FALSE")
            expr_sub = expr_sub.replace("1", "TRUE")
            with logicparse(expr_sub, gateH = 1.1, outlabel="output") as d:
                d.save(f'gen/circuit{i}.svg')
            return 1
        except:
            print("failed")
            print(traceback.format_exc())
            return 0

def draw_preprocessing(expr):
    print(expr)
    new_expr = ""
    i = 0
    print((len(expr) - 3))
    while i < (len(expr) - 3):
        print(f"{expr[i]} is the current under investigation")
        if expr[i+1] == expr[i+3] and (expr[i+1] == '&' or expr[i+1] == '|'):
            new_expr = new_expr + "(" + expr[i:i+3] + ")"
            i += 3

        # elif expr[i] == expr[i+2] and (expr[i] == '&' or expr[i] == '|'):
        #     new_expr = new_expr + expr[i] + "(" + expr[i+1:i+4] + ")"
        #     i += 4

        else:
            new_expr += expr[i]
            i += 1
    new_expr = new_expr + expr[i+1:len(expr)]
    print(new_expr)
    return new_expr

def eda_wrapper(args_dict):
    # global config_dict
    # config_dict = args_dict
    for key in args_dict:
        config_dict[key] = args_dict[key]

    dummy = args_dict['dummy']
    input_num = args_dict['input_num']
    # config_dict['dummy'] = dummy
    # config_dict['input_num'] = input_num
    print('---------------------------')
    print(f'DUMMY = {dummy}, INPUT = {input_num}')
    if dummy < 10:
        dummy = f'0{dummy}'
    if input_num < 10:
        input_num = f'0{input_num}'
    output_file = f'D{dummy}N{input_num}.csv'
    main_loop(config_dict, output_file)

class Blob:
    def __init__(self, output, answer, complexity):
        self.output = output
        self.answer = answer
        self.complexity = complexity

class Transform:
    def __init__(self, name, trans_func):
        self.name = name
        self.trans_func = trans_func

# draw_preprocessing("A&B&C")
# # netlist("(A&B)&(C&D)", 0)
