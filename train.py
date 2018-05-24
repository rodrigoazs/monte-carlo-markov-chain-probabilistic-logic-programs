# -*- coding: utf-8 -*-
"""
Created on Wed May 23 16:06:41 2018

@author: 317005
"""

from satisfy import *
from main import *
from state import *
from sklearn.metrics import mean_squared_error    
import math     
import random
from itertools import product

class MCPLP:
    def __init__(self):
        self.target = target
        self.examples = []
        self.data = []
        self.bases = []
        self.state = []
        self.evaluations = {}
        self.max_literals = 5
        
        self.temp_values = []
        self.cost_values = []
    
    def set_target(self, target):
        self.target = target
        
    def set_max_literals(self, max_literals):
        self.max_literals = max_literals
        
    def load_examples(self, file):
        data = []
        with open(file) as f:
            for line in f:
                m = re.search('^(\w+)\(([\w, ]+)*\).$', line)
                if m:
                    probability = 1
                    relation = m.group(1).replace(' ', '')
                    entities = m.group(2).replace(' ', '').split(',')
                    if relation == self.target:
                        data.append([relation, entities, probability])
                p = re.search('^([0-9.]+)::(\w+)\(([\w, ]+)*\).$', line)
                if p:
                    probability = float(p.group(1).replace(' ', ''))
                    relation = p.group(2).replace(' ', '')
                    entities = p.group(3).replace(' ', '').split(',')
                    if relation == self.target:
                        data.append([relation, entities, probability])
        self.examples = data
    
    def load_data(self, file):
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
                    if relation != self.target:
                        data.append([relation, entities, probability])
                p = re.search('^([0-9.]+)::(\w+)\(([\w, ]+)*\).$', line)
                if p:
                    probability = float(p.group(1).replace(' ', ''))
                    relation = p.group(2).replace(' ', '')
                    entities = p.group(3).replace(' ', '').split(',')
                    if relation != self.target:
                        data.append([relation, entities, probability])
        self.data = data
        self.bases = bases

    def get_mse(self, clause):
        y = []
        y_pred = []
        for example in self.examples:
            y.append(example[2])
            varA = EnAtom(example[1][0])
            varB = EnAtom(example[1][1])
            y_pred.append(self.monte_carlo_delta(delta_p = 0.01, m=100, clause=clause, variables={EnVariable('A'): varA, EnVariable('B'): varB}))
        return mean_squared_error(y, y_pred)
    
    def sample_program(self):
        program = EnStructure()
        for base in self.bases:
            program.add_base(base[0], base[1])   
        for dt in self.data:
            if random.random() < dt[2]:
                program.add_tuple(dt[0], dt[1])
        return program
                
    def monte_carlo(self, m=1000, clause=[], variables={}):
        if len(clause) == 0:
            return 1.0
        mn = 0
        for i in range(m):   
            program = self.sample_program()
            mn += program.satisfy_clause_recursive(clause, variables=variables)
        return mn / m

    def monte_carlo_delta(self, delta_p = 0.01, m=1000, clause=[], variables={}):
        if len(clause) == 0:
            return 1.0
        c = 0
        i = 0
        p = 0
        delta = 1
        while delta > delta_p:
            program = self.sample_program()
            result = program.satisfy_clause_recursive(clause, variables=variables)
            c += result
            i += 1
            if i % m == 0:
                p = c/i
                delta = 2 * math.sqrt(p*(1-p)/i)
        #print('Samples generated: '+str(i))
        #print('Result: '+str(p))
        return p
    
    def get_variables_type(self, clause):
        bases_dict = dict(self.bases)
        
        vrs = {}
        lastVar = 'B'
        for i in range(len(bases_dict[self.target])):
            if bases_dict[self.target][i] not in vrs:
                vrs[bases_dict[self.target][i]] = set()
            vrs[bases_dict[self.target][i]].add(chr(65 + i))
            
        for cl in clause:
            pred = str(cl[0])
            for j in range(len(cl[1:])):
                if bases_dict[pred][j] not in vrs:
                    vrs[bases_dict[pred][j]] = set()
                vrs[bases_dict[pred][j]].add(str(cl[1:][j]))
                if str(cl[1:][j]) > lastVar:
                    lastVar = str(cl[1:][j])
                
        return (vrs, lastVar)
    
    def get_possible_candidates(self, clause):
        candidates = []
        
        if len(clause) == 0:
            possible_literals = self.get_possible_literals([])
            for cl in possible_literals:
                a = clause.copy()
                a.append(cl)
                candidates.append(a)
            candidates.append([])
            return candidates
        else:
            if len(clause) < self.max_literals:
                after_possible_literals = self.get_possible_literals(clause)
                for cl in after_possible_literals:
                    a = clause.copy()
                    allow = True
                    for lit in a:
                        if self.print_clause([lit]) == self.print_clause([cl]):
                            allow = False
                            break
                    if allow:
                        a.append(cl)
                        candidates.append(a)
            possible_literals = self.get_possible_literals(clause[:-1])
            for cl in possible_literals:
                a = clause[:-1].copy()
                allow = True
                for lit in a:
                    if self.print_clause([lit]) == self.print_clause([cl]):
                        allow = False
                        break
                if allow:
                    a.append(cl)
                    candidates.append(a)
            before_possible_literals = self.get_possible_literals(clause[:-2])
            for cl in before_possible_literals:
                a = clause[:-2].copy()
                allow = True
                for lit in a:
                    if self.print_clause([lit]) == self.print_clause([cl]):
                        allow = False
                        break
                if allow:
                    a.append(cl)
                    candidates.append(a)
            if len(clause[:-2]) == 0:
                candidates.append([])
            return candidates     
                    
    def get_possible_literals(self, clause):
        bases_dict = dict(self.bases)
        vrs = self.get_variables_type(clause)
        
        possibles = []
        for key, value in bases_dict.items():
            if key != self.target:
                if len(bases_dict[key]) == 1:
                    v = vrs[0][bases_dict[key][0]]
                    for i in v:
                        possibles.append([EnPredicate(key), EnVariable(i)])
                    possibles.append([EnPredicate(key), EnVariable(chr(ord(vrs[1])+1))])
                else:
                    v1 = vrs[0][bases_dict[key][0]]
                    v2 = vrs[0][bases_dict[key][1]]
                    p = list(product(v1, v2))
                    for i in p:
                        possibles.append([EnPredicate(key), EnVariable(i[0]), EnVariable(i[1])])
                    for i in v1:
                        possibles.append([EnPredicate(key), EnVariable(i), EnVariable(chr(ord(vrs[1])+1))])
                    for i in v2:
                        possibles.append([EnPredicate(key), EnVariable(chr(ord(vrs[1])+1)), EnVariable(i)])      
        return possibles
    
    def sample_candidate(self):
        candidates = self.get_possible_candidates(self.state)
        candidate= random.choice(candidates)            
        return candidate
        
#    def sample_candidate(self):
#        bases_dict = dict(self.bases)
#        
#        if len(self.state) >= 5:
#            candidate = self.state.copy()
#            candidate = candidate[:-1]
#            return candidate
#        
#        possibles = []
#        if len(self.state) == 0:
#            last = self.target
#        else:
#            last = self.state[-1]
#        
#        if last[0] == '_': #is inverse function
#            right = 0
#            last = last[1:]
#        else:
#            right = 1
#        
#        if len(self.state) == 0 or len(bases_dict[last]) == 1:
#            right = 0
#        
##        clause = self.state_to_clause(self.state)
##        str_clause = self.print_clause(clause)
##        if str_clause not in self.evaluations:
##            mse = self.get_mse(clause)
##            self.evaluations[str_clause] = mse
#        
#        for key, value in bases_dict.items():
#            if key != self.target:
#                if value[0] == bases_dict[last][right]:
#                    possibles.append(key)
#                if len(value) > 1 and value[1] == bases_dict[last][right]:
#                    possibles.append('_' + key)
#
##        for i in range(len(possibles)):
##            temp = self.state.copy()
##            temp.append(possibles[i])
##            clause = self.state_to_clause(temp)
##            str_clause = self.print_clause(clause)
##            if str_clause not in self.evaluations:
##                mse = self.get_mse(clause)
##                self.evaluations[str_clause] = mse
##            
##        if len(state):
##            if random.random() < 0.5:
##                self.state = self.state[:-1]
##            else:
##                self.state.append(random.choice(possibles))
##        else:
##            self.state.append(random.choice(possibles))
#
#        if random.random() < 1/(len(possibles)+1):
#            candidate = self.state.copy()
#            candidate = candidate[:-1]
#        else:
#            candidate = self.state.copy()
#            candidate.append(random.choice(possibles))
#            
#        return candidate
        
    def calculate_state_mse(self, state):
        #clause = self.state_to_clause(state)
        clause = state
        str_clause = self.print_clause(clause)
        if str_clause not in self.evaluations:
            mse = self.get_mse(clause)
            self.evaluations[str_clause] = mse
        return self.evaluations[str_clause]
        
    def state_to_clause(self, state):
        if len(state) == 0:
            return []

        bases_dict = dict(self.bases)
        
        variables = ['A']
        a = [chr(i) for i in range(67, 67 + len(state))]
        variables.extend(a)
        
        t = []
        v = 0
        for i in range(len(state)):
            pred = state[i][1:] if state[i][0] == '_' else state[i]
            vl = [variables[v + j] for j in range(len(bases_dict[pred]))]
            v += 1 if len(bases_dict[pred]) > 1 else 0
            t.append([state[i], vl])
        
        if len(t[-1][1]) == 1:
            target_types = bases_dict[pred][0]
            pred = t[-1][0][1:] if t[-1][0][0] == '_' else t[-1][0]
            pred_types = bases_dict[pred][0]
            if target_types == pred_types:
                t[-1][1][0] = 'B' 
        else:
            if t[-1][0][0] == '_':
                pred = t[-1][0][1:]
                target_types = bases_dict[self.target][1]
                pred_types = bases_dict[pred][0]
                if target_types == pred_types:
                    t[-1][1][1] = 'B' 
            else:
                pred = t[-1][0]
                target_types = bases_dict[self.target][1]
                pred_types = bases_dict[pred][1]
                if target_types == pred_types:
                    t[-1][1][1] = 'B' 
        
        for i in range(len(t)):
            if t[i][0][0] == '_':
                t[i][1] = t[i][1][::-1]
                t[i][0] = t[i][0][1:]
            pred = t[i][0]
            varsb = [EnVariable(j) for j in t[i][1]]
            t[i] = [EnPredicate(pred)]
            t[i].extend(varsb)

        return t

    def print_clause(self, clause):
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
    
    def print_state(self, state):
        #print(self.state)
        return self.print_clause(self.state_to_clause(state))
    
    def clauses_visited(self):
        clauses = self.evaluations.items()
        clauses = sorted(clauses, key=lambda x: x[1])
        return clauses
    
    def calculate_temp(self, iteration):
        return 1000 * 1 / (1 + math.exp((iteration - 0) / 60))
    
    def annealing_process(self, n_iterations):
        for i in range(n_iterations):
            temp = self.calculate_temp(i)
            
            candidate = self.sample_candidate()
            candidate_mse = self.calculate_state_mse(candidate)
            
            state_mse = self.calculate_state_mse(self.state)
            
            self.cost_values.append(state_mse)
            self.temp_values.append(temp)
            
            if temp > 0:
                try:
                    ratio = math.exp((state_mse - candidate_mse) / temp)
                except:
                    ratio = 1
            else:
                ratio = int(candidate_mse < state_mse)
                
            if random.random() < ratio:
                self.state = candidate

mc = MCPLP()
mc.set_target('grandmother')
mc.load_data('data/family_prob.txt')
mc.load_examples('data/family_examples.txt')