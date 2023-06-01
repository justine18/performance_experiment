import timeit
import pandas as pd
import numpy as np
import gurobipy as gpy


########## Intuitive Gurobi ##########
def run_intuitive_gurobi(I, IJK, JKL, KLM, solve, repeats, number):
    setup = {
        "I": I,
        "IJK": IJK,
        "JKL": JKL,
        "KLM": KLM,
        "solve": solve,
        "model_function": intuitive_gurobi,
    }
    r = timeit.repeat(
        "model_function(I, IJK, JKL, KLM, solve)",
        repeat=repeats,
        number=number,
        globals=setup,
    )

    result = pd.DataFrame(
        {
            "IJK": [len(IJK)],
            "I": [len(I)],
            "Language": ["Intuitive GurobiPy"],
            "MinTime": [np.min(r)],
            "MeanTime": [np.mean(r)],
            "MedianTime": [np.median(r)],
        }
    )
    return result


def intuitive_gurobi(I, IJK, JKL, KLM, solve):
    model = gpy.Model()

    x = model.addVars(
        [
            (i, j, k, l, m)
            for (i, j, k) in IJK
            for (jj, kk, l) in JKL
            if (jj == j) and (kk == k)
            for (kkk, ll, m) in KLM
            if (kkk == k) and (ll == l)
        ],
        name="x",
    )

    model.setObjective(1, gpy.GRB.MINIMIZE)

    model.addConstrs(
        (
            gpy.quicksum(
                x[i, j, k, l, m]
                for (ii, j, k) in IJK
                if (ii == i)
                for (jj, kk, l) in JKL
                if (jj == j) and (kk == k)
                for (kkk, ll, m) in KLM
                if (kkk == k) and (ll == l)
            )
            >= 0
            for i in I
        ),
        "ei",
    )

    model.update()

    if solve:
        model.Params.OutputFlag = 0
        model.Params.TimeLimit = 0
        model.optimize()


########## Gurobi ##########
def run_gurobi(I, ijk, jkl, klm, solve, repeats, number):
    # convert sets to tuplelists
    IJK = gpy.tuplelist(ijk)
    JKL = gpy.tuplelist(jkl)
    KLM = gpy.tuplelist(klm)

    setup = {
        "I": I,
        "IJK": IJK,
        "JKL": JKL,
        "KLM": KLM,
        "solve": solve,
        "model_function": gurobi,
    }
    r = timeit.repeat(
        "model_function(I, IJK, JKL, KLM, solve)",
        repeat=repeats,
        number=number,
        globals=setup,
    )

    result = pd.DataFrame(
        {
            "IJK": [len(ijk)],
            "I": [len(I)],
            "Language": ["GurobiPy"],
            "MinTime": [np.min(r)],
            "MeanTime": [np.mean(r)],
            "MedianTime": [np.median(r)],
        }
    )
    return result


def gurobi(I, IJK, JKL, KLM, solve):
    model = gpy.Model()

    x_list = [
        (i, j, k, l, m)
        for (i, j, k) in IJK.select("*", "*", "*")
        for (j, k, l) in JKL.select(j, k, "*")
        for (k, l, m) in KLM.select(k, l, "*")
    ]

    x = model.addVars(x_list, name="x")

    model.setObjective(1, gpy.GRB.MINIMIZE)

    model.addConstrs(
        (
            gpy.quicksum(
                x[i, j, k, l, m]
                for (i, j, k) in IJK.select(i, "*", "*")
                for (j, k, l) in JKL.select(j, k, "*")
                for (k, l, m) in KLM.select(k, l, "*")
            )
            >= 0
            for i in I
        ),
        "ei",
    )

    model.update()

    if solve:
        model.Params.OutputFlag = 0
        model.Params.TimeLimit = 0
        model.optimize()
