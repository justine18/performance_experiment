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
def run_pyomo(I, L, M, IJ, JK, IK, KL, LM, D, solve, repeats, number):
    setup = {
        "I": I,
        "L": L,
        "M": M,
        "IJ": IJ,
        "JK": JK,
        "IK": IK,
        "KL": KL,
        "LM": LM,
        "D": D,
        "solve": solve,
        "model_function": pyomo,
    }
    r = timeit.repeat(
        "model_function(I, L, M, IJ, JK, IK, KL, LM, D, solve)",
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


def pyomo(I, L, M, IJ, JK, IK, KL, LM, D, solve):
    model = pyo.ConcreteModel()

    model.I = pyo.Set(initialize=I)
    model.L = pyo.Set(initialize=L)
    model.M = pyo.Set(initialize=M)
    model.IJ = pyo.Set(initialize=IJ)
    model.JK = pyo.Set(initialize=JK)
    model.IK = pyo.Set(initialize=IK)
    model.KL = pyo.Set(initialize=KL)
    model.LM = pyo.Set(initialize=LM)

    # some data wrangling
    IJ_dict = defaultdict(set)
    for i, j in IJ:
        IJ_dict[i].add(j)
    KJ_dict = defaultdict(set)
    for j, k in JK:
        KJ_dict[k].add(j)
    # make a dictionary of (i, k) : {(i, j, k) tuples}
    IK_IJK = {
        (i, k): {(i, j, k) for j in IJ_dict.get(i, set()) & KJ_dict.get(k, set())}
        for (i, k) in IK
    }

    L_M = {l: [] for l in model.L}
    L_M.update(
        {
            l: list(map(itemgetter(1), lm))
            for l, lm in itertools.groupby(sorted(model.LM), itemgetter(0))
        }
    )
    M_L = {m: [] for m in model.M}
    M_L.update(
        {
            m: list(map(itemgetter(0), lm))
            for m, lm in itertools.groupby(
                sorted(model.LM, key=itemgetter(1)), itemgetter(1)
            )
        }
    )
    L_K = {l: [] for l in model.L}
    L_K.update(
        {
            l: list(map(itemgetter(0), kl))
            for l, kl in itertools.groupby(
                sorted(model.KL, key=itemgetter(1)), itemgetter(1)
            )
        }
    )

    model.L_M = pyo.Set(model.L, initialize=L_M)
    model.M_L = pyo.Set(model.M, initialize=M_L)
    model.L_K = pyo.Set(model.L, initialize=L_K)
    model.IK_IJK = pyo.Set(IK_IJK.keys(), initialize=IK_IJK)

    model.f = pyo.Param(default=1)
    model.d = pyo.Param(model.I, model.M, initialize=D)

    x_list = list(itertools.chain(*IK_IJK.values()))

    model.x = pyo.Var(x_list, domain=pyo.NonNegativeReals)

    model.y = pyo.Var(
        [(i, k, l) for i in model.I for (k, l) in model.KL], domain=pyo.NonNegativeReals
    )

    model.z = pyo.Var(
        [(i, l, m) for i in model.I for (l, m) in model.LM], domain=pyo.NonNegativeReals
    )

    model.OBJ = pyo.Objective(expr=model.f)

    model.production = pyo.Constraint(IK_IJK.keys(), rule=production_rule)
    model.transport = pyo.Constraint(model.I, model.L, rule=transport_rule)
    model.demand = pyo.Constraint(model.I, model.M, rule=demand_rule)

    # model.write("int.lp")

    if solve:
        opt = pyo.SolverFactory("gurobi")
        opt.solve(model, timelimit=0)


def production_rule(model, i, k):
    lhs = [model.x[i, j, k] for i, j, k in model.IK_IJK[i, k]]
    rhs = [model.y[i, k, l] for (kk, l) in model.KL if kk == k]

    if lhs and rhs:
        return sum(lhs) >= sum(rhs)
    else:
        return pyo.Constraint.Skip


def transport_rule(model, i, l):
    if len(model.L_K[l]) or len(model.L_M[l]):
        return sum(model.y[i, k, l] for k in model.L_K[l]) >= sum(
            model.z[i, l, m] for m in model.L_M[l]
        )
    return pyo.Constraint.Skip


def demand_rule(model, i, m):
    return sum(model.z[i, l, m] for l in model.M_L[m]) >= model.d[i, m]
