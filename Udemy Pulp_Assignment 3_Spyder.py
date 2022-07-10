# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
from pulp import *

distmatrix = pd.read_excel('warehouse_city.xlsx')
distmatrix

distmatrix.set_index('Warehouse', inplace=True)
distmatrix

keys = [(w, c) for w in distmatrix.index for c in distmatrix.columns]  # list comprehension
keys

dist_dict = {(w, c): distmatrix.loc[w, c] for w in distmatrix.index for c in
             distmatrix.columns}  # dictionary comprehension
dist_dict

demand_dict = dict(zip(distmatrix.columns, [10000, 20000, 33000, 9000, 60000, 2500, 35000]))
demand_dict

warehouse = distmatrix.index
customers = distmatrix.columns

flows = LpVariable.dicts('flows', keys, cat='Binary')
open_w = LpVariable.dicts('open_w', distmatrix.index, cat='Binary')

# creating a model for running optimization
model = LpProblem('transportprob', sense=LpMinimize)

# defining the objective function
model += lpSum([demand_dict.get(c) * flows[(w, c)] * dist_dict.get((w, c)) for w in open_w for c in distmatrix.columns])

# defining constraints
for c in customers:
    model += lpSum([flows.get((w, c)) for w in warehouse]) == 1

model += lpSum([open_w[w] for w in warehouse]) == 3

for w in warehouse:
    for c in customers:
        model += open_w[w] >= flows.get((w, c))

model.solve()
