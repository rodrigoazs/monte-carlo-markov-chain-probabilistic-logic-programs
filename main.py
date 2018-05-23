#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 22 21:12:04 2018

@author: rodrigoazs
"""

import re
import math
import random
from satisfy import *

def load_data(file):
    data = []
    bases = []
    with open(file) as f:
        for line in f:
            a = re.search('^base\((\w+)\(([\w, ]+)*\)\).$', line)
            if a:
                relation = a.group(1).replace(' ', '')
                entities = a.group(2).replace(' ', '').split(',')
                bases.append([relation, entities])
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
    return [data, bases]

def state_to_clause(state):
    if len(state) == 0:
        return []
    clause = []
    if len(state) == 1:
        if state[0][0] == '_':
            clause.append([EnPredicate(state[0][1:]), EnVariable('B'), EnVariable('A')])
        else:
            clause.append([EnPredicate(state[0]), EnVariable('A'), EnVariable('B')])
        return clause
    lastVar = 67
    if state[0][0] == '_':
        clause.append([EnPredicate(state[0][1:]), EnVariable(chr(lastVar)), EnVariable('A')])
    else:
        clause.append([EnPredicate(state[0]), EnVariable('A'), EnVariable(chr(lastVar))])
    for i in range(1, len(state)-1):
        if state[i][0] == '_':
            clause.append([EnPredicate(state[i][1:]), EnVariable(chr(lastVar+1)), EnVariable(chr(lastVar))])
        else:
            clause.append([EnPredicate(state[i]), EnVariable(chr(lastVar)), EnVariable(chr(lastVar+1))])
        lastVar += 1
    if state[-1][0] == '_':
        clause.append([EnPredicate(state[-1][1:]), EnVariable('B'), EnVariable(chr(lastVar))])
    else:
        clause.append([EnPredicate(state[-1]), EnVariable(chr(lastVar)), EnVariable('B')])
    return clause

def print_clause(clause):
    if len(clause) == 0:
        return 'True'
    c = []
    for i in clause:
        args = []
        for j in i[1:]:
            args.append(str(j))
        args = ','.join(args)
        c.append(str(i[0]) + '(' + args + ')')
    return ','.join(c) 
    
def sample_program(data, bases):
    program = EnStructure()
    for base in bases:
        program.add_base(base[0], base[1])   
    for dt in data:
        if random.random() < dt[2]:
            program.add_tuple(dt[0], dt[1])
    return program
                
def monte_carlo(m=1000, clause=[], variables={}, data=[], bases=[]):
    if len(clause) == 0:
        return 1.0
    mn = 0
    for i in range(m):   
        program = sample_program(data, bases)
        mn += program.satisfy_clause_recursive(clause, variables=variables)
    return mn / m

def monte_carlo_delta(delta_p = 0.01, m=1000, clause=[], variables={}, data=[], bases=[]):
    if len(clause) == 0:
        return 1.0
    c = 0
    i = 0
    p = 0
    delta = 1
    while delta > delta_p:
        program = sample_program(data, bases)
        result = program.satisfy_clause_recursive(clause, variables=variables)
        c += result
        i += 1
        if i % m == 0:
            p = c/i
            delta = 2 * math.sqrt(p*(1-p)/i)
    print('Samples generated: '+str(i))
    return p
#for base in bases:
#    program.add_base(base[0], base[1])
#    
#for dt in data:
#    program.add_tuple(dt[0], dt[1])
#    
#program.satisfy_clause_recursive([[EnPredicate('parent'), EnVariable('A'), EnVariable('B')]], variables={EnVariable('A'): EnAtom('bart'), EnVariable('B'): EnAtom('stijn')})

#data = load_data('data/family_prob.txt')
#a = monte_carlo(m=1000, clause=[[EnPredicate('parent'), EnVariable('A'), EnVariable('C')],[EnPredicate('parent'), EnVariable('C'), EnVariable('B')],[EnPredicate('male'), EnVariable('A')]], variables={EnVariable('A'): EnAtom('rene'), EnVariable('B'): EnAtom('lieve')}, data=data[0], bases=data[1])

#a = monte_carlo_delta(delta_p = 0.01, m=1000, clause=[[EnPredicate('parent'), EnVariable('A'), EnVariable('C')],[EnPredicate('parent'), EnVariable('C'), EnVariable('B')],[EnPredicate('male'), EnVariable('A')]], variables={EnVariable('A'): EnAtom('rene'), EnVariable('B'): EnAtom('lieve')}, data=data[0], bases=data[1])