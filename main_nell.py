#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 22 21:12:04 2018

@author: rodrigoazs
"""

from train import *
import logging
import json

print('Start MCPLP')
mc = MCPLP(target='athleteplaysforteam', max_literals=2, level=logging.DEBUG)
mc.load_data('data/nell/athleteplaysforteam/nell_athleteplaysforteam_facts.txt')
mc.load_examples('data/nell/athleteplaysforteam/nell_athleteplaysforteam_examples_small.txt')
results = mc.annealing_process(1000)


a = mc.monte_carlo_delta(delta_p = 0.01, m=100, clause=[[EnPredicate('athleteledsportsteam'), EnVariable('A'), EnVariable('B')]], variables={EnVariable('A'): EnAtom('al_harrington'), EnVariable('B'): EnAtom('knicks')})


import matplotlib.pyplot as plt

plt.plot([i for i in range(len(results[1]))], results[1])

plt.plot([i for i in range(len(results[2]))], results[2])

plt.loglog([i for i in range(len(results[2]))], results[2])

with open('results/grandmother_4_results.txt', 'w') as outfile:  
    json.dump(results, outfile)
    
with open('results/grandmother_4_clauses.txt', 'w') as outfile:  
    json.dump(mc.clauses_visited(), outfile)