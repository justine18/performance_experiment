import pyomo.environ as pyo
import logging
import timeit
import pandas as pd
import numpy as np
import itertools
from collections import defaultdict
from operator import itemgetter

logging.getLogger("pyomo.core").setLevel(logging.ERROR)


########## Intuitive Pyomo ##########
def run_intuitive_pyomo(I, IK, IL, IM, IJK, IKL, ILM, D, solve, repeats, number):
    setup = {
        "IK": IK,
        "IL": IL,
        "IM": IM,
        "IJK": IJK,
        "IKL": IKL,
        "ILM": ILM,
        "D": D,
        "solve": solve,
        "model_function": intuitive_pyomo,
    }
    r = timeit.repeat(
        "model_function(IK, IL, IM, IJK, IKL, ILM, D, solve)",
        repeat=repeats,
        number=number,
        globals=setup,
    )

    result = pd.DataFrame(
        {
            "I": [len(I)],
            "Language": ["Intuitive Pyomo"],
            "MinTime": [np.min(r)],
            "MeanTime": [np.mean(r)],
            "MedianTime": [np.median(r)],
        }
    )
    return result


def intuitive_pyomo(IK, IL, IM, IJK, IKL, ILM, D, solve):
    model = pyo.ConcreteModel()

    model.IK = pyo.Set(initialize=IK)
    model.IL = pyo.Set(initialize=IL)
    model.IM = pyo.Set(initialize=IM)
    model.IJK = pyo.Set(initialize=IJK)
    model.IKL = pyo.Set(initialize=IKL)
    model.ILM = pyo.Set(initialize=ILM)

    model.f = pyo.Param(default=1)
    model.d = pyo.Param(model.IM, initialize=D)

    model.x = pyo.Var(model.IJK, domain=pyo.NonNegativeReals)
    model.y = pyo.Var(model.IKL, domain=pyo.NonNegativeReals)
    model.z = pyo.Var(model.ILM, domain=pyo.NonNegativeReals)

    model.OBJ = pyo.Objective(expr=model.f)

    model.production = pyo.Constraint(model.IK, rule=intuitive_production_rule)
    model.transport = pyo.Constraint(model.IL, rule=intuitive_transport_rule)
    model.demand = pyo.Constraint(model.IM, rule=intuitive_demand_rule)

    # model.write("int.lp")

    if solve:
        opt = pyo.SolverFactory("gurobi")
        opt.solve(model, timelimit=0)


def intuitive_production_rule(model, i, k):
    return sum(
        model.x[i, j, k] for (ii, j, kk) in model.IJK if ii == i and kk == k
    ) >= sum(model.y[i, k, l] for (ii, kk, l) in model.IKL if ii == i and kk == k)


def intuitive_transport_rule(model, i, l):
    return sum(
        model.y[i, k, l] for (ii, k, ll) in model.IKL if ii == i and ll == l
    ) >= sum(model.z[i, l, m] for (ii, ll, m) in model.ILM if ii == i and ll == l)


def intuitive_demand_rule(model, i, m):
    return (
        sum(model.z[i, l, m] for (ii, l, mm) in model.ILM if ii == i and mm == m)
        >= model.d[i, m]
    )


########## Pyomo ##########
def run_pyomo(I, IK, IL, IM, IJK, IKL, ILM, IK_IJK, IK_IKL, IL_IKL, IL_ILM, IM_ILM, D, solve, repeats, number):
    setup = {
        "IK": IK,
        "IL": IL,
        "IM": IM,
        "IJK": IJK,
        "IKL": IKL,
        "ILM": ILM,
        "IK_IJK": IK_IJK,
        "IK_IKL": IK_IKL,
        "IL_IKL": IL_IKL,
        "IL_ILM": IL_ILM,
        "IM_ILM": IM_ILM,
        "D": D,
        "solve": solve,
        "model_function": pyomo,
    }
    r = timeit.repeat(
        "model_function(IK, IL, IM, IJK, IKL, ILM, IK_IJK, IK_IKL, IL_IKL, IL_ILM, IM_ILM, D, solve)",
        repeat=repeats,
        number=number,
        globals=setup,
    )

    result = pd.DataFrame(
        {
            "I": [len(I)],
            "Language": ["Pyomo"],
            "MinTime": [np.min(r)],
            "MeanTime": [np.mean(r)],
            "MedianTime": [np.median(r)],
        }
    )
    return result


def pyomo(IK, IL, IM, IJK, IKL, ILM, IK_IJK, IK_IKL, IL_IKL, IL_ILM, IM_ILM, D, solve):
    model = pyo.ConcreteModel()

    model.IK = pyo.Set(initialize=IK)
    model.IL = pyo.Set(initialize=IL)
    model.IM = pyo.Set(initialize=IM)
    model.IJK = pyo.Set(initialize=IJK)
    model.IKL = pyo.Set(initialize=IKL)
    model.ILM = pyo.Set(initialize=ILM)

    model.IK_IJK = pyo.Set(IK_IJK.keys(), initialize=IK_IJK)
    model.IK_IKL = pyo.Set(IK_IKL.keys(), initialize=IK_IKL)
    model.IL_IKL = pyo.Set(IL_IKL.keys(), initialize=IL_IKL)
    model.IL_ILM = pyo.Set(IL_ILM.keys(), initialize=IL_ILM)
    model.IM_ILM = pyo.Set(IM_ILM.keys(), initialize=IM_ILM)

    model.f = pyo.Param(default=1)
    model.d = pyo.Param(model.IM, initialize=D)

    model.x = pyo.Var(model.IJK, domain=pyo.NonNegativeReals)
    model.y = pyo.Var(model.IKL, domain=pyo.NonNegativeReals)
    model.z = pyo.Var(model.ILM, domain=pyo.NonNegativeReals)

    model.OBJ = pyo.Objective(expr=model.f)

    model.production = pyo.Constraint(model.IK, rule=production_rule)
    model.transport = pyo.Constraint(model.IL, rule=transport_rule)
    model.demand = pyo.Constraint(model.IM, rule=demand_rule)

    # model.write("int.lp")

    if solve:
        opt = pyo.SolverFactory("gurobi")
        opt.solve(model, timelimit=0)


def production_rule(model, i, k):
    return sum(model.x[ijk] for ijk in model.IK_IJK[i, k]) >= sum(
        model.y[ikl] for ikl in model.IK_IKL[i, k]
    )


def transport_rule(model, i, l):
    return sum(model.y[ikl] for ikl in model.IL_IKL[i, l]) >= sum(
        model.z[ilm] for ilm in model.IL_ILM[i, l]
    )


def demand_rule(model, i, m):
    return sum(model.z[ilm] for ilm in model.IM_ILM[i, m]) >= model.d[i, m]
