# -*- coding: utf-8 -*-
"""
Created on Wed May 23 16:06:41 2018

@author: 317005
"""

import logging
import math
import random
import re
import time
from itertools import product

from sklearn.metrics import mean_squared_error

from satisfy import *


class MCPLP:
    def __init__(
        self,
        target="",
        max_literals=5,
        delta_p=0.01,
        m=100,
        level="WARNING",
        amplitude=1000,
        center=0,
        width=50,
    ):
        self.examples = []
        self.data = []
        self.bases = []
        self.state = []
        self.evaluations = {}

        self.max_literals = max_literals
        self.target = target
        self.delta_p = delta_p
        self.m = m
        self.amplitude = amplitude
        self.center = center
        self.width = width

        self.fixed_program = None

        logging.basicConfig(level=level)
        self.logger = logging.getLogger("mcplp")
        # self.logger.setLevel('INFO')

    def print_parameters(self, run_time):
        return "\n".join(
            [
                "Max literals: " + str(self.max_literals),
                "Target: " + self.target,
                "Delta p: " + str(self.delta_p),
                "M: " + str(self.m),
                "Curve Amplitude: " + str(self.amplitude),
                "Curve Center: " + str(self.center),
                "Curve Width: " + str(self.width),
                "Run time: " + str(run_time),
            ]
        )

    def load_examples(self, file):
        data = []
        with open(file) as f:
            for line in f:
                m = re.search("^(\w+)\(([\w, ]+)*\).$", line)
                if m:
                    probability = 1
                    relation = m.group(1).replace(" ", "")
                    entities = m.group(2).replace(" ", "").split(",")
                    if relation == self.target:
                        data.append([relation, entities, probability])
                p = re.search("^([0-9.]+)::(\w+)\(([\w, ]+)*\).$", line)
                if p:
                    probability = float(p.group(1).replace(" ", ""))
                    relation = p.group(2).replace(" ", "")
                    entities = p.group(3).replace(" ", "").split(",")
                    if relation == self.target:
                        data.append([relation, entities, probability])
        self.examples = data

    def load_data(self, file):
        data = []
        bases = []
        with open(file) as f:
            for line in f:
                a = re.search("^base\((\w+)\(([\w, ]+)*\)\).$", line)
                if a:
                    relation = a.group(1).replace(" ", "")
                    entities = a.group(2).replace(" ", "").split(",")
                    bases.append([relation, entities])
                m = re.search("^(\w+)\(([\w, ]+)*\).$", line)
                if m:
                    probability = 1
                    relation = m.group(1).replace(" ", "")
                    entities = m.group(2).replace(" ", "").split(",")
                    if relation != self.target:
                        data.append([relation, entities, probability])
                p = re.search("^([0-9.]+)::(\w+)\(([\w, ]+)*\).$", line)
                if p:
                    probability = float(p.group(1).replace(" ", ""))
                    relation = p.group(2).replace(" ", "")
                    entities = p.group(3).replace(" ", "").split(",")
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
            # start = time.time()
            pred = self.monte_carlo_delta(
                delta_p=self.delta_p,
                m=self.m,
                clause=clause,
                variables={EnVariable("A"): varA, EnVariable("B"): varB},
            )
            # run_time = time.time() - start
            y_pred.append(pred)
            # self.logger.info('Result for example %s is %s, Time: %s' % (str(example), str(pred), str(run_time)))
        return mean_squared_error(y, y_pred)

    def sample_program(self):
        program = EnStructure()
        for base in self.bases:
            program.add_base(base[0], base[1])
        for dt in self.data:
            if random.random() < dt[2]:
                program.add_tuple(dt[0], dt[1])
        return program

    def get_program(self):
        if self.fixed_program == None:
            program = EnStructure()
            for base in self.bases:
                program.add_base(base[0], base[1])
            for dt in self.data:
                # if random.random() < dt[2]:
                program.add_tuple(dt[0], dt[1], dt[2])
            self.fixed_program = program
        return self.fixed_program

    def monte_carlo(self, m=100, clause=[], variables={}):
        if len(clause) == 0:
            return 1.0
        mn = 0
        for i in range(m):
            program = self.get_program()
            mn += program.satisfy_clause_recursive_prob(clause, variables=variables)
        return mn / m

    def monte_carlo_delta(self, delta_p=0.01, m=100, clause=[], variables={}):
        # start = time.time()
        if len(clause) == 0:
            return 1.0
        c = 0
        i = 0
        p = 0
        delta = 1
        while delta > delta_p:
            program = self.get_program()
            result = program.satisfy_clause_recursive_prob(clause, variables=variables)
            c += result
            i += 1
            if i % m == 0:
                p = c / i
                delta = 2 * math.sqrt(p * (1 - p) / i)
                # print('Samples generated: '+str(i))
        # run_time = time.time() - start
        # self.logger.info('Samples generated: %s, Result: %s, Clause: %s, Time: %s' % (str(i), str(p), self.print_clause(clause), str(run_time)))
        return p

    def get_variables_type(self, clause):
        bases_dict = dict(self.bases)

        vrs = {}
        lastVar = "B"
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
                    if bases_dict[key][0] in vrs[0]:
                        v = vrs[0][bases_dict[key][0]]
                        for i in v:
                            possibles.append([EnPredicate(key), EnVariable(i)])
                        # mode only + (previous variables)
                        # possibles.append([EnPredicate(key), EnVariable(chr(ord(vrs[1])+1))])
                else:
                    if bases_dict[key][0] in vrs[0] and bases_dict[key][1] in vrs[0]:
                        v1 = vrs[0][bases_dict[key][0]]
                        v2 = vrs[0][bases_dict[key][1]]
                        p = list(product(v1, v2))
                        for i in p:
                            possibles.append(
                                [EnPredicate(key), EnVariable(i[0]), EnVariable(i[1])]
                            )
                        for i in v1:
                            possibles.append(
                                [
                                    EnPredicate(key),
                                    EnVariable(i),
                                    EnVariable(chr(ord(vrs[1]) + 1)),
                                ]
                            )
                        for i in v2:
                            possibles.append(
                                [
                                    EnPredicate(key),
                                    EnVariable(chr(ord(vrs[1]) + 1)),
                                    EnVariable(i),
                                ]
                            )
                    elif bases_dict[key][0] in vrs[0]:
                        v1 = vrs[0][bases_dict[key][0]]
                        for i in v1:
                            possibles.append(
                                [
                                    EnPredicate(key),
                                    EnVariable(i),
                                    EnVariable(chr(ord(vrs[1]) + 1)),
                                ]
                            )
                    elif bases_dict[key][1] in vrs[0]:
                        v2 = vrs[0][bases_dict[key][1]]
                        for i in v2:
                            possibles.append(
                                [
                                    EnPredicate(key),
                                    EnVariable(chr(ord(vrs[1]) + 1)),
                                    EnVariable(i),
                                ]
                            )
        return possibles

    def sample_candidate(self):
        candidates = self.get_possible_candidates(self.state)
        candidate = random.choice(candidates)
        return candidate

    def calculate_state_mse(self, state):
        clause = state
        str_clause = self.print_clause(clause)
        if str_clause not in self.evaluations:
            mse = self.get_mse(clause)
            self.evaluations[str_clause] = mse
        return self.evaluations[str_clause]

    def print_clause(self, clause):
        if len(clause) == 0:
            return "True"
        c = []
        for i in clause:
            args = []
            for j in i[1:]:
                args.append(str(j))
            args = ",".join(args)
            c.append(str(i[0]) + "(" + args + ")")
        return ",".join(c)

    def clauses_visited(self):
        clauses = self.evaluations.items()
        clauses = sorted(clauses, key=lambda x: x[1])
        return clauses

    def calculate_temp(self, iteration):
        return (
            self.amplitude * 1 / (1 + math.exp((iteration - self.center) / self.width))
        )

    def annealing_process(self, n_iterations):
        self.logger.info("Starting Simulated Annealing")

        state_values = []
        temp_values = []
        cost_values = []
        start = time.time()

        try:
            for i in range(n_iterations):
                temp = self.calculate_temp(i)

                candidate = self.sample_candidate()
                candidate_mse = self.calculate_state_mse(candidate)

                state_mse = self.calculate_state_mse(self.state)

                cost_values.append(state_mse)
                temp_values.append(temp)

                self.logger.info(
                    "Iteration: %s, Temperature: %s State MSE: %s, Candidate MSE: %s, State: %s, Candidate: %s"
                    % (
                        i,
                        temp,
                        state_mse,
                        candidate_mse,
                        self.print_clause(self.state),
                        self.print_clause(candidate),
                    )
                )

                if temp > 0:
                    try:
                        ratio = math.exp((state_mse - candidate_mse) / temp)
                    except:
                        ratio = 1
                else:
                    ratio = int(candidate_mse < state_mse)

                if random.random() < ratio:
                    self.state = candidate
                    state_values.append(self.print_clause(self.state))
        except KeyboardInterrupt:
            self.logger.info("LEARNING INTERRUPTED BY USER")

        run_time = time.time() - start
        self.logger.info("Total Run Time: %s" % (str(run_time)))
        return (
            self.print_parameters(run_time),
            temp_values,
            cost_values,
            state_values,
            self.clauses_visited(),
        )
