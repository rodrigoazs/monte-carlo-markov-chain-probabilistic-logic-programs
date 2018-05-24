# -*- coding: utf-8 -*-
"""
Created on Wed May 23 16:06:41 2018

@author: 317005
"""

from satisfy import *
from main import *
from state import *
from sklearn.metrics import mean_squared_error           

class MCPLP:
    def __init__(self):
        self.target = target
        self.examples = []
        self.data = []
        self.bases = []
        self.state = []
        self.evaluations = {}
    
    def set_target(self, target):
        self.target = target
        
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
            print(varA)
            print(varB)
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
        print('Samples generated: '+str(i))
        print('Result: '+str(p))
        return p
        
    def next_state(self):
        bases_dict = dict(self.bases)
        
        possibles = []
        if len(self.state) == 0:
            last = self.target
        else:
            last = state[-1]
        
        if last[0] == '_': #is inverse function
            right = 0
            last = last[1:]
        else:
            right = 1
        
        if len(state) == 0 or len(bases_dict[last]) == 1:
            right = 0
        
        clause = self.state_to_clause(self.state)
        str_clause = self.print_clause(clause)
        if str_clause not in self.evaluations:
            mse = self.get_mse(clause)
            self.evaluations[str_clause] = mse
        
        for key, value in bases_dict.items():
            if key != target:
                if value[0] == bases_dict[last][right]:
                    possibles.append(key)
                if len(value) > 1 and value[1] == bases_dict[last][right]:
                    possibles.append('_' + key)
        print(possibles)
        for i in range(len(possibles)):
            temp = self.state.copy()
            temp.append(possibles[i])
            clause = self.state_to_clause(temp)
            str_clause = self.print_clause(clause)
            if str_clause not in self.evaluations:
                mse = self.get_mse(clause)
                self.evaluations[str_clause] = mse
            
        if len(state):
            if random.random() < 0.5:
                self.state = self.state[:-1]
            else:
                self.state.append(random.choice(possibles))
        else:
            self.state.append(random.choice(possibles))
            
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

mc = MCPLP()
mc.set_target('athleteplayssport')
mc.load_data('data/nell.txt')
mc.load_examples('data/nell.txt')

mc.monte_carlo_delta(clause=[[EnPredicate('parent'), EnVariable('A'), EnVariable('C')],[EnPredicate('parent'), EnVariable('C'), EnVariable('B')]], variables={EnVariable('A'): EnAtom('rene'), EnVariable('B'): EnAtom('lieve')})
      
#examples = load_examples('data/family_examples.txt')
#data = load_data('data/family_prob.txt')



#target = 'grandmother'
state = []
state = next_state(state, target, data)

cl = state_to_clause(state)

get_mse(examples, cl, data)

d = get_mse(examples, [], data)
a = get_mse(examples, [[EnPredicate('parent'), EnVariable('A'), EnVariable('C')]], data)
b = get_mse(examples, [[EnPredicate('parent'), EnVariable('C'), EnVariable('A')]], data)