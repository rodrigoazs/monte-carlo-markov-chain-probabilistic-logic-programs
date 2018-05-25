#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 22 21:12:04 2018

@author: rodrigoazs
"""

from train import *

mc = MCPLP(target='grandmother', level=logging.INFO)
mc.load_data('data/family_prob.txt')
mc.load_examples('data/family_examples.txt')

mc.annealing_process(500)