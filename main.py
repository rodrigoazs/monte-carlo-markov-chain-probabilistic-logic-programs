#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 22 21:12:04 2018

@author: rodrigoazs
"""

import re
from satisfy import *

data = []
bases = []
program = EnStructure()

with open('data/family.txt') as f:
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
            
for base in bases:
    program.add_base(base[0], base[1])
    
for dt in data:
    program.add_tuple(dt[0], dt[1])
    
program.satisfy_clause_recursive([[EnPredicate('parent'), EnVariable('A'), EnVariable('B')]], variables={EnVariable('A'): EnAtom('bart'), EnVariable('B'): EnAtom('stijn')})