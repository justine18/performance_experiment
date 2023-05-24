import pyomo.environ as pyo
import logging
import timeit
import pandas as pd
import numpy as np

logging.getLogger("pyomo.core").setLevel(logging.ERROR)


########## Intuitive Pyomo ##########
def run_intuitive_pyomo(I, L, M, IJ, JK, IK, KL, LM, D, solve, repeats, number):
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
        "model_function": intuitive_pyomo,
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
            "Language": ["Intuitive Pyomo"],
            "MinTime": [np.min(r)],
            "MeanTime": [np.mean(r)],
            "MedianTime": [np.median(r)],
        }
    )
    return result


def intuitive_pyomo(I, L, M, IJ, JK, IK, KL, LM, D, solve):
    model = pyo.ConcreteModel()

    model.I = pyo.Set(initialize=I)
    model.L = pyo.Set(initialize=L)
    model.M = pyo.Set(initialize=M)
    model.IJ = pyo.Set(initialize=IJ)
    model.JK = pyo.Set(initialize=JK)
    model.IK = pyo.Set(initialize=IK)
    model.KL = pyo.Set(initialize=KL)
    model.LM = pyo.Set(initialize=LM)

    model.f = pyo.Param(default=1)
    model.d = pyo.Param(model.I, model.M, initialize=D)

    model.x = pyo.Var(
        [
            (i, j, k)
            for (i, j) in model.IJ
            for (jj, k) in model.JK
            if jj == j
            for (ii, kk) in model.IK
            if (ii == i) and (kk == k)
        ],
        domain=pyo.NonNegativeReals,
    )

    model.y = pyo.Var(
        [(i, k, l) for i in model.I for (k, l) in model.KL], domain=pyo.NonNegativeReals
    )

    model.z = pyo.Var(
        [(i, l, m) for i in model.I for (l, m) in model.LM], domain=pyo.NonNegativeReals
    )

    model.OBJ = pyo.Objective(expr=model.f)

    model.production = pyo.Constraint(model.IK, rule=intuitive_production_rule)
    model.transport = pyo.Constraint(model.I, model.L, rule=intuitive_transport_rule)
    model.demand = pyo.Constraint(model.I, model.M, rule=intuitive_demand_rule)

    # model.write("int.lp")

    if solve:
        opt = pyo.SolverFactory("gurobi")
        opt.solve(model)


def intuitive_production_rule(model, i, k):
    lhs = [
        model.x[i, j, k]
        for (ii, j) in model.IJ
        if ii == i
        for (jj, kk) in model.JK
        if (jj == j) and (kk == k)
    ]
    rhs = [model.y[i, k, l] for (kk, l) in model.KL if kk == k]

    if lhs or rhs:
        return sum(lhs) >= sum(rhs)
    else:
        return pyo.Constraint.Skip


def intuitive_transport_rule(model, i, l):
    lhs = [model.y[i, k, l] for (k, ll) in model.KL if ll == l]
    rhs = [model.z[i, l, m] for (lll, m) in model.LM if lll == l]

    if lhs or rhs:
        return sum(lhs) >= sum(rhs)
    else:
        return pyo.Constraint.Skip


def intuitive_demand_rule(model, i, m):
    return sum(model.z[i, l, m] for (l, mm) in model.LM if mm == m) >= model.d[i, m]
