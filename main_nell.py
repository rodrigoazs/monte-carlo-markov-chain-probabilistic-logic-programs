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
mc = MCPLP(target='athleteplaysforteam', delta_p=0.1, m=10, max_literals=2, amplitude=1000, width=500, level='WARNING')
mc.load_data('data/nell/athleteplaysforteam/nell_athleteplaysforteam_facts.txt')
mc.load_examples('data/nell/athleteplaysforteam/nell_athleteplaysforteam_examples.txt')
results = mc.annealing_process(5000)


#a = mc.monte_carlo_delta(delta_p = 0.1, m=50, clause=[[EnPredicate('athleteledsportsteam'), EnVariable('A'), EnVariable('B')]], variables={EnVariable('A'): EnAtom('pat_burrell'), EnVariable('B'): EnAtom('phillies')})

#def calculate_temp( iteration):
#    return 1000 * 1 / (1 + math.exp((iteration - 0) / 500))
#t = []
#x = []
#for i in range(5000):
#    x.append(i)
#    t.append(calculate_temp(i))
    
#import matplotlib.pyplot as plt

#plt.plot(x, t)

#plt.plot([i for i in range(len(results[1]))], results[1])

#plt.plot([i for i in range(len(results[2]))], results[2])

#plt.loglog([i for i in range(len(results[2]))], results[2])

with open('results/athleteplaysforteam_results.txt', 'w') as outfile:  
    json.dump(results, outfile)
    
with open('results/athleteplaysforteam_clauses.txt', 'w') as outfile:  
    json.dump(mc.clauses_visited(), outfile)