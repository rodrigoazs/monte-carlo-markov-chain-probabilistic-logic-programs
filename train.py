# -*- coding: utf-8 -*-
"""
Created on Wed May 23 16:06:41 2018

@author: 317005
"""

from main import *
from state import *
from sklearn.metrics import mean_squared_error

def load_examples(file):
    data = []
    with open(file) as f:
        for line in f:
            m = re.search('^(\w+)\(([\w, ]+)*\).$', line)
            if m:
                probability = 1
                relation = m.group(1).replace(' ', '')
                entities = m.group(2).replace(' ', '').split(',')
                data.append([relation, entities, probability])
            p = re.search('^([0-9.]+)::(\w+)\(([\w, ]+)*\).$', line)
            if p:
                probability = float(p.group(1).replace(' ', ''))
                relation = p.group(2).replace(' ', '')
                entities = p.group(3).replace(' ', '').split(',')
                data.append([relation, entities, probability])
    return data                
                
examples = load_examples('data/family_examples.txt')
data = load_data('data/family_prob.txt')

def get_mse(examples, clause, data):
    y = []
    y_pred = []
    for example in examples:
        y.append(example[2])
        varA = EnAtom(example[1][0])
        varB = EnAtom(example[1][1])
        print(varA)
        print(varB)
        y_pred.append(monte_carlo_delta(delta_p = 0.01, m=100, clause=clause, variables={EnVariable('A'): varA, EnVariable('B'): varB}, data=data[0], bases=data[1]))
    return mean_squared_error(y, y_pred)

target = 'grandmother'
state = []
state = next_state(state, target, data)

cl = state_to_clause(state)

get_mse(examples, cl, data)
print(get_mse(examples, c, data))