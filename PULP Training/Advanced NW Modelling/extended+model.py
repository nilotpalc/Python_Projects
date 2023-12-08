#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 21:33:53 2020

@author: haythamomar
"""
import inventorize as inv
import pandas as pd
from pulp import *

inbound = pd.read_excel('inbound.xlsx')

inbound = inbound.set_index('DCS')
demand = pd.read_excel('demand.xlsx')
demand = demand.set_index('shop')
outbound = pd.read_excel('outbound.xlsx')
outbound = outbound.set_index('DCS')
plant_costs = pd.read_excel('plant costs.xlsx')
plant_costs = plant_costs.set_index('plant')
DC_costs = pd.read_excel('DC_costs.xlsx')
DC_costs = DC_costs.set_index('DCS')
DC_costs['Capacity'] = 10000

plants = plant_costs.index
DCs = DC_costs.index
shops = demand.index

inbound_keys = [(w, p) for w in DCs for p in plants]
outbound_keys = [(w, s) for w in DCs for s in shops]

inbound_var = LpVariable.dicts('inbound', inbound_keys, 0, None, 'Integer')
outbound_var = LpVariable.dicts('outbound', outbound_keys, 0, None, 'Integer')
open_dc = LpVariable.dicts('open_dc', DCs, cat='Binary')
open_plant = LpVariable.dicts('open_p', plants, cat='Binary')

inbound_cost = lpSum(inbound_var[(w, p)] * inbound.loc[w, p] for p in plants for w in DCs)
outbound_cost = lpSum(outbound_var[(w, s)] * outbound.loc[w, s] for w in DCs for s in shops)
production_cost = lpSum(inbound_var[(w, p)] * plant_costs.loc[p, 'Var'] for p in plants for w in DCs)
opening_plant_cost = lpSum(open_plant[(p)] * plant_costs.loc[p, 'fixed cost'] for p in plants)
opening_dc_cost = lpSum(open_dc[(w)] * DC_costs.loc[w, 'Fixed Cost'] for w in DCs)
dc_operaing_cost = lpSum(inbound_var[(w, p)] * DC_costs.loc[w, 'Variable Cost'] for w in DCs for p in plants)

model = LpProblem('Extended', LpMinimize)

model += (inbound_cost + outbound_cost + production_cost + opening_plant_cost + opening_dc_cost + dc_operaing_cost)

#### demand cosntratins

for s in shops:
    model += lpSum(outbound_var[(w, s)] for w in DCs) >= demand.loc[s, 'Demand']

#### capacity constraints

for p in plants:
    model += lpSum(inbound_var[(w, p)] for w in DCs) <= lpSum(plant_costs.loc[p, 'capacity'] * open_plant[(p)])

for w in DCs:
    model += lpSum(inbound_var[(w, p)] for p in plants) <= lpSum(DC_costs.loc[w, 'Capacity'] * open_dc[(w)])

#### flow constraints

for w in DCs:
    model += lpSum(inbound_var[(w, p)] for p in plants) == lpSum(outbound_var[(w, s)] for s in shops)

### opening constraints

model += lpSum(open_dc[(w)] for w in DCs) == 1

model += lpSum(open_plant[(p)] for p in plants) >= 1
model += lpSum(open_plant[(p)] for p in plants) <= 3

model.solve()

for v in model.variables():
    print(v.name, "=", v.varValue)

len(model.variables())

###getting variables which are bigger than 0
[{v.name: v.varValue} for v in model.variables() if v.varValue > 0]

total_demand = sum(demand['Demand'])

dist_matrix = {(w, s): 1 if outbound.loc[w, s] <= 80 else 0 for w in DCs for s in shops}

current_service_level = lpSum(
    outbound_var[(w, s)].varValue * dist_matrix[(w, s)] for w in DCs for s in shops) / total_demand

#### model with multiple DCs

model_relaxed = LpProblem('Extended1', LpMinimize)

model_relaxed += (
            inbound_cost + outbound_cost + production_cost + opening_plant_cost + opening_dc_cost + dc_operaing_cost)

#### demand cosntratins

for s in shops:
    model_relaxed += lpSum(outbound_var[(w, s)] for w in DCs) >= demand.loc[s, 'Demand']

#### capacity constraints

for p in plants:
    model_relaxed += lpSum(inbound_var[(w, p)] for w in DCs) <= lpSum(plant_costs.loc[p, 'capacity'] * open_plant[(p)])

for w in DCs:
    model_relaxed += lpSum(inbound_var[(w, p)] for p in plants) <= lpSum(DC_costs.loc[w, 'Capacity'] * open_dc[(w)])

#### flow constraints

for w in DCs:
    model_relaxed += lpSum(inbound_var[(w, p)] for p in plants) == lpSum(outbound_var[(w, s)] for s in shops)

### opening constraints

model_relaxed += lpSum(open_dc[(w)] for w in DCs) >= 1
model_relaxed += lpSum(open_dc[(w)] for w in DCs) <= 9

model_relaxed += lpSum(open_plant[(p)] for p in plants) >= 1
model_relaxed += lpSum(open_plant[(p)] for p in plants) <= 3

##service level constraint

model_relaxed += lpSum(outbound_var[(w, s)] * dist_matrix[(w, s)] for w in DCs for s in shops) / total_demand >= 0.95

model_relaxed.solve()

for v in model_relaxed.variables():
    print(v.name, "=", v.varValue)

total_demand = sum(demand['Demand'])

dist_matrix = {(w, s): 1 if outbound.loc[w, s] <= 80 else 0 for w in DCs for s in shops}

current_service_level = lpSum(
    outbound_var[(w, s)].varValue * dist_matrix[(w, s)] for w in DCs for s in shops) / total_demand

model_relaxed.writeLP('exttended_model.txt')

binding = [{'constraint': name, 'slack': c.slack} for name, c in model_relaxed.constraints.items()]
