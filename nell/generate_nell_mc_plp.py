# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 18:30:31 2018

@author: Rodrigo Azevedo
"""


import random
import re
import time
from itertools import product

# Importing the libraries
import pandas as pd


def recursive(root, target, depth=0):
    facts = set()
    if depth == 4:
        for relation in root.relations:
            if relation.name != target:
                if relation.inverse == False:
                    facts.add(
                        ",".join(
                            [
                                relation.origin.name,
                                relation.name,
                                relation.node.name,
                                str(relation.probability)[:6],
                            ]
                        )
                    )
                else:
                    facts.add(
                        ",".join(
                            [
                                relation.node.name,
                                relation.name,
                                relation.origin.name,
                                str(relation.probability)[:6],
                            ]
                        )
                    )
        return facts
    else:
        for relation in root.relations:
            if relation.name != target:
                # print(str(relation))
                if relation.inverse == False:
                    facts.add(
                        ",".join(
                            [
                                relation.origin.name,
                                relation.name,
                                relation.node.name,
                                str(relation.probability)[:6],
                            ]
                        )
                    )
                else:
                    facts.add(
                        ",".join(
                            [
                                relation.node.name,
                                relation.name,
                                relation.origin.name,
                                str(relation.probability)[:6],
                            ]
                        )
                    )
                to_add = recursive(relation.node, target, depth + 1)
                facts = facts.union(to_add)
        return facts


class Relation:
    def __init__(self, origin, node, name, inverse=False, probability=1.0):
        self.name = name
        self.inverse = inverse
        self.probability = probability
        self.node = node
        self.origin = origin

    def __str__(self):
        if self.inverse == False:
            return (
                str(self.probability)
                + "::"
                + self.name
                + "("
                + str(self.origin)
                + ","
                + str(self.node)
                + ")."
            )
        else:
            return (
                str(self.probability)
                + "::"
                + self.name
                + "("
                + str(self.node)
                + ","
                + str(self.origin)
                + ")."
            )


class Node:
    def __init__(self, name):
        self.name = name
        self.relations = []

    def __str__(self):
        return self.name

    def add_relation(self, relation, obj, inverse=False, probability=1.0):
        self.relations.append(
            Relation(self, obj, relation, inverse=inverse, probability=probability)
        )


class Graph:
    def __init__(self):
        self.nodes = {}
        self.count = {}

    def add_relation(self, sub, relation, obj, probability):
        if sub not in self.nodes:
            self.nodes[sub] = Node(sub)
            self.count[sub] = 0
        if obj not in self.nodes:
            self.nodes[obj] = Node(obj)
            self.count[obj] = 0
        # only for athletes
        if (
            relation == "athleteplaysinleague"
            or relation == "athleteplaysforteam"
            or relation == "athleteplayssport"
        ):
            self.count[sub] += 1
            # self.count[obj] += 1
        sub = self.nodes[sub]
        obj = self.nodes[obj]

        sub.add_relation(relation, obj, probability=probability)
        obj.add_relation(relation, sub, inverse=True, probability=probability)


def create_folds(data, size):
    length = int(len(data) / size)  # length of each fold
    folds = []
    for i in range((size - 1)):
        folds += [data[i * length : (i + 1) * length]]
    folds += [data[(size - 1) * length : len(data)]]
    return folds


def get_data(
    dataset, n_folds, target, target_parity, allow_negation=True, example_mode="balance"
):
    # relations_accepted = ['athleteplayssport','teamalsoknownas','athleteplaysforteam','teamplayssport']
    settings = ""
    base = ""
    folds = [""] * n_folds

    relations = {}
    graph = Graph()
    for data in dataset.values:
        entity_type = (data[1].split(":"))[1]
        entity = (data[1].split(":"))[2]
        probability = data[3]
        relation = (data[4].split(":"))[1]
        value_type = (data[5].split(":"))[1]
        value = (data[5].split(":"))[2]

        entity = entity.lower()  # .replace('_', '')
        value = value.lower()  # .replace('_', '')
        # re.sub('[^a-zA-Z]', '', title[j])
        entity = re.sub("[^a-z_]", "", entity)
        value = re.sub("[^a-z_]", "", value)

        # entity and value cannot start with '_', otherwise it is considered variable (?)
        entity = entity[1:] if entity[0] == "_" else entity
        value = value[1:] if value[0] == "_" else value

        graph.add_relation(entity, relation, value, probability)
        if relation in relations:
            relations[relation].append(
                [entity, relation, value, probability, entity_type, value_type]
            )
        else:
            relations[relation] = [
                [entity, relation, value, probability, entity_type, value_type]
            ]

    #    for relation in relations:
    #        if relation != target:
    #            settings += 'mode('+str(relation)+'(+,+)).\n'
    #            settings += 'mode('+str(relation)+'(+,-)).\n'
    #            settings += 'mode('+str(relation)+'(-,+)).\n'
    #    settings += '\n'
    sorted_x = sorted(graph.count.items(), key=lambda x: x[1], reverse=True)
    accepted_entities = set()
    for i in range(100):
        accepted_entities.add(sorted_x[i][0])
    # facts = recursive(graph.nodes[first], target, 0)

    for key, value in relations.items():
        first = value[0]
        settings += (
            "base("
            + str(first[1])
            + "("
            + str(first[4])
            + ","
            + str(first[5])
            + ")).\n"
        )
    settings += "\n"
    #    if allow_negation == False:
    #        settings += 'option(negation,off).\n'
    #    settings += '\n'
    #    settings += 'learn('+target+'/'+str(target_parity)+').\n'
    #    if example_mode != 'balance_incode':
    #        settings += '\n'
    #        settings += 'example_mode('+ example_mode +').\n'
    #    settings += '\n'

    for key, value in relations.items():
        for d in value:
            if d[1] != target:
                base += (
                    str(d[3])[:6]
                    + "::"
                    + str(d[1])
                    + "("
                    + str(d[0])
                    + ","
                    + str(d[2])
                    + ").\n"
                )

    # tar = relations[target]
    tar = []
    for relation in relations[target]:
        if relation[0] in accepted_entities:
            tar.append(relation)
    values = [set(), set()]
    for d in tar:
        values[0].add(str(d[0]))
        values[1].add(str(d[2]))

    # random.shuffle(tar)
    # tar = create_folds(tar, n_folds)
    pos_count = len(tar)
    random.shuffle(tar)
    tar = create_folds(tar, n_folds)
    neg_examples = list(product(*values))
    random.shuffle(neg_examples)
    neg_examples = neg_examples[:pos_count]
    neg_examples = create_folds(neg_examples, n_folds)

    for i in range(n_folds):
        # print positive and negative targets
        for j in range(len(tar[i])):
            d = tar[i][j]
            # print(str(d[0]) + ' count ' + str(base.count(str(d[0]))))
            if base.count(str(d[0])) > 2:
                folds[i] += (
                    str(d[3])[:6]
                    + "::"
                    + str(d[1])
                    + "("
                    + str(d[0])
                    + ","
                    + str(d[2])
                    + ").\n"
                )
            # rand_objects = all_objects.difference(tuples[str(d[0])])
            # folds[i] += '0.0::'+str(d[1]) + '(' +str(d[0])+ ','+str(random.choice(list(rand_objects)))+ ').\n'
            if example_mode == "balance_incode":
                if base.count(str(neg_examples[i][j][0])) > 2:
                    folds[i] += (
                        "0.0::"
                        + str(d[1])
                        + "("
                        + str(neg_examples[i][j][0])
                        + ","
                        + neg_examples[i][j][1]
                        + ").\n"
                    )

    return {"settings": settings, "base": base, "folds": folds, "graph": graph}


dataset = pd.read_csv("NELL.sports.08m.850.small.csv")
n_folds = 1
# ============================================

targets = [
    ("athleteplaysinleague", 2),
    # ('teamplaysinleague', 2),
    ("athleteplaysforteam", 2),
    # ('teamalsoknownas', 2),
    # ('athleteledsportsteam', 2),
    # ('teamplaysagainstteam', 2),
    # ('teamplayssport', 2),
    ("athleteplayssport", 2),
]

for tg in targets:
    data = get_data(dataset, 1, tg[0], tg[1], example_mode="balance_incode")
    with open("nell_" + tg[0] + "_facts.txt", "w") as file:
        file.write(data["settings"])
        file.write(data["base"])
    with open("nell_" + tg[0] + "_examples.txt", "w") as file:
        file.write(data["folds"][0])
#    # cross-validation
#    for i in range(n_folds):
#        settings = data['settings']
#        train = data['base']
#        test = data['base']
#        for j in range(n_folds):
#            if j == i:
#                test += data['folds'][j]
#            else:
#                train += data['folds'][j]
#        probfoil(settings=settings, train=train, test=test, l=5, verbose=1, allow_negation=False, example_mode='balance_incode')
#    time_total = time.time() - time_start
#    print ('\nCross-validation finished')
#    print ('Total time:\t%.4fs' % time_total)
#    print ('\n')
#
