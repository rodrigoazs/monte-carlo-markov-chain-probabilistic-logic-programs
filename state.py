# -*- coding: utf-8 -*-
"""
Created on Wed May 23 16:44:38 2018

@author: 317005
"""

import random
#data = load_data('data/family_prob.txt')

def next_state(state, target, data):
    bases_dict = dict(data[1])
    
    possibles = []
    if len(state) == 0:
        last = target
    else:
        last = state[-1]
    
    if last[0] == '_': #is inverse function
        right = 0
        last = last[1:]
    else:
        right = 1
    
    if len(state) == 0 or len(bases_dict[last]) == 1:
        right = 0
    
    for key, value in bases_dict.items():
        if key != target:
            if value[0] == bases_dict[last][right]:
                possibles.append(key)
            if len(value) > 1 and value[1] == bases_dict[last][right]:
                possibles.append('_' + key)
            
    if len(state):
        if random.random() < 0.5:
            state = state[:-1]
        else:
            state.append(random.choice(possibles))
    else:
        state.append(random.choice(possibles))
        
    return state