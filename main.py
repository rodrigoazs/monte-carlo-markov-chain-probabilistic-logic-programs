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