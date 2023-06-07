import pyomo.environ as pyo
import logging
import timeit
import pandas as pd
import numpy as np
import itertools, operator

logging.getLogger("pyomo.core").setLevel(logging.ERROR)


########## Intuitive Pyomo ##########
def run_intuitive_pyomo(I, IJK, JKL, KLM, solve, repeats, number):
    setup = {
        "I": I,
        "IJK": IJK,
        "JKL": JKL,
        "KLM": KLM,
        "solve": solve,
        "model_function": intuitive_pyomo,
    }
    r = timeit.repeat(
        "model_function(I, IJK, JKL, KLM, solve)",
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


def intuitive_pyomo(I, IJK, JKL, KLM, solve):
    model = pyo.ConcreteModel()

    model.I = pyo.Set(initialize=I)
    model.IJK = pyo.Set(initialize=IJK)
    model.JKL = pyo.Set(initialize=JKL)
    model.KLM = pyo.Set(initialize=KLM)

    model.z = pyo.Param(default=1)

    model.x = pyo.Var(
        [
            (i, j, k, l, m)
            for (i, j, k) in model.IJK
            for (jj, kk, l) in model.JKL
            if (jj == j) and (kk == k)
            for (kkk, ll, m) in model.KLM
            if (kkk == k) and (ll == l)
        ],
        domain=pyo.NonNegativeReals,
    )

    model.OBJ = pyo.Objective(expr=model.z)

    model.ei = pyo.Constraint(model.I, rule=intuitive_ei_rule)

    if solve:
        opt = pyo.SolverFactory("gurobi")
        opt.solve(model, options={"TimeLimit": 0}, load_solutions=False)


def intuitive_ei_rule(model, i):
    lhs = [
        model.x[i, j, k, l, m]
        for (ii, j, k) in model.IJK
        if (ii == i)
        for (jj, kk, l) in model.JKL
        if (jj == j) and (kk == k)
        for (kkk, ll, m) in model.KLM
        if (kkk == k) and (ll == l)
    ]
    if len(lhs) < 2:
        return pyo.Constraint.Skip
    else:
        return sum(lhs) >= 0


########## Pyomo ##########
def run_pyomo(I, IJK, JKL, KLM, solve, repeats, number):
    setup = {
        "I": I,
        "IJK": IJK,
        "JKL": JKL,
        "KLM": KLM,
        "solve": solve,
        "model_function": pyomo,
    }
    r = timeit.repeat(
        "model_function(I, IJK, JKL, KLM, solve)",
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


def pyomo(I, IJK, JKL, KLM, solve):
    model = pyo.ConcreteModel()

    model.I = pyo.Set(initialize=I)

    x_list = [
        (i, j, k, l, m) for (i, j, k) in IJK for l in JKL[j, k] for m in KLM[k, l]
    ]

    constraint_dict_i = {i: [] for i in I}
    constraint_dict_i.update(
        {
            i: list(j)
            for i, j in itertools.groupby(sorted(x_list), operator.itemgetter(0))
        }
    )

    model.x_list = pyo.Set(initialize=x_list)
    model.c_dict_i = pyo.Set(model.I, initialize=constraint_dict_i)

    model.z = pyo.Param(default=1)

    model.x = pyo.Var(model.x_list, domain=pyo.NonNegativeReals)

    model.OBJ = pyo.Objective(expr=model.z)

    model.ei = pyo.Constraint(model.I, rule=ei_rule)

    if solve:
        opt = pyo.SolverFactory("gurobi")
        opt.solve(model, options={"TimeLimit": 0}, load_solutions=False)


def ei_rule(model, i):
    if not model.c_dict_i[i]:
        return pyo.Constraint.Skip
    return sum(model.x[idx] for idx in model.c_dict_i[i]) >= 0


########## Intuitive Pyomo ##########
def run_cartesian_pyomo(I, J, K, L, M, IJK, JKL, KLM, solve, repeats, number):
    setup = {
        "I": I,
        "J": J,
        "K": K,
        "L": L,
        "M": M,
        "IJK": IJK,
        "JKL": JKL,
        "KLM": KLM,
        "solve": solve,
        "model_function": cartesian_pyomo,
    }
    r = timeit.repeat(
        "model_function(I, J, K, L, M, IJK, JKL, KLM, solve)",
        repeat=repeats,
        number=number,
        globals=setup,
    )

    result = pd.DataFrame(
        {
            "I": [len(I)],
            "Language": ["Cartesian Pyomo"],
            "MinTime": [np.min(r)],
            "MeanTime": [np.mean(r)],
            "MedianTime": [np.median(r)],
        }
    )
    return result


def cartesian_pyomo(I, J, K, L, M, IJK, JKL, KLM, solve):
    model = pyo.ConcreteModel()

    model.I = pyo.Set(initialize=I)
    model.J = pyo.Set(initialize=J)
    model.K = pyo.Set(initialize=K)
    model.L = pyo.Set(initialize=L)
    model.M = pyo.Set(initialize=M)
    model.IJK = pyo.Set(initialize=IJK)
    model.JKL = pyo.Set(initialize=JKL)
    model.KLM = pyo.Set(initialize=KLM)

    model.z = pyo.Param(default=1)

    model.x = pyo.Var(
        model.I,
        model.J,
        model.K,
        model.L,
        model.M,
        domain=pyo.NonNegativeReals,
    )

    model.OBJ = pyo.Objective(expr=model.z)

    model.ei = pyo.Constraint(model.I, rule=intuitive_ei_rule)

    if solve:
        opt = pyo.SolverFactory("gurobi")
        opt.solve(model, options={"TimeLimit": 0}, load_solutions=False)
