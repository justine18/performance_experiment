import timeit
import pandas as pd
import numpy as np
import gurobipy as gpy


########## Intuitive Gurobi ##########
def run_intuitive_gurobi(I, ik, il, im, ijk, ikl, ilm, D, solve, repeats, number):
    # convert sets to tuplelists
    IK = gpy.tuplelist(ik)
    IL = gpy.tuplelist(il)
    IM = gpy.tuplelist(im)
    IJK = gpy.tuplelist(ijk)
    IKL = gpy.tuplelist(ikl)
    ILM = gpy.tuplelist(ilm)
    d = gpy.tupledict(D)

    setup = {
        "IK": IK,
        "IL": IL,
        "IM": IM,
        "IJK": IJK,
        "IKL": IKL,
        "ILM": ILM,
        "D": d,
        "solve": solve,
        "model_function": intuitive_gurobi,
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
            "Language": ["Intuitive GurobiPy"],
            "MinTime": [np.min(r)],
            "MeanTime": [np.mean(r)],
            "MedianTime": [np.median(r)],
        }
    )
    return result


def intuitive_gurobi(IK, IL, IM, IJK, IKL, ILM, d, solve):
    model = gpy.Model()

    x = model.addVars(IJK, name="x")
    y = model.addVars(IKL, name="y")
    z = model.addVars(ILM, name="z")

    model.setObjective(1, gpy.GRB.MINIMIZE)

    model.addConstrs(
        gpy.quicksum(x[i, j, k] for (i, j, k) in IJK.select(i, "*", k))
        >= gpy.quicksum(y[i, k, l] for (i, k, l) in IKL.select(i, k, "*"))
        for (i, k) in IK
    )

    model.addConstrs(
        gpy.quicksum(y[i, k, l] for (i, k, l) in IKL.select(i, "*", l))
        >= gpy.quicksum(z[i, l, m] for (i, l, m) in ILM.select(i, l, "*"))
        for (i, l) in IL
    )

    model.addConstrs(
        gpy.quicksum(z[i, l, m] for (i, l, m) in ILM.select(i, "*", m)) >= d[i, m]
        for (i, m) in IM
    )

    model.update()

    if solve:
        model.Params.OutputFlag = 0
        model.Params.TimeLimit = 0
        model.optimize()


########## Gurobi ##########
def run_gurobi(
    I,
    ik,
    il,
    im,
    ijk,
    ikl,
    ilm,
    ik_ijk,
    ik_ikl,
    il_ikl,
    il_ilm,
    im_ilm,
    D,
    solve,
    repeats,
    number,
):
    # convert sets to tuplelists
    IK = gpy.tuplelist(ik)
    IL = gpy.tuplelist(il)
    IM = gpy.tuplelist(im)
    IJK = gpy.tuplelist(ijk)
    IKL = gpy.tuplelist(ikl)
    ILM = gpy.tuplelist(ilm)
    # IK_IJK = gpy.tupledict(ik_ijk)
    # IK_IKL = gpy.tupledict(ik_ikl)
    setup = {
        "IK": IK,
        "IL": IL,
        "IM": IM,
        "IJK": IJK,
        "IKL": IKL,
        "ILM": ILM,
        "IK_IJK": ik_ijk,
        "IK_IKL": ik_ikl,
        "IL_IKL": il_ikl,
        "IL_ILM": il_ilm,
        "IM_ILM": im_ilm,
        "D": D,
        "solve": solve,
        "model_function": gurobi,
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
            "Language": ["GurobiPy"],
            "MinTime": [np.min(r)],
            "MeanTime": [np.mean(r)],
            "MedianTime": [np.median(r)],
        }
    )
    return result


def gurobi(IK, IL, IM, IJK, IKL, ILM, IK_IJK, IK_IKL, IL_IKL, IL_ILM, IM_ILM, d, solve):
    model = gpy.Model()

    x = model.addVars(IJK, name="x")
    y = model.addVars(IKL, name="y")
    z = model.addVars(ILM, name="z")

    model.setObjective(1, gpy.GRB.MINIMIZE)

    model.addConstrs(
        gpy.quicksum(x[ijk] for ijk in IK_IJK[i, k])
        >= gpy.quicksum(y[ikl] for ikl in IK_IKL[i, k])
        for (i, k) in IK
    )

    model.addConstrs(
        gpy.quicksum(y[ikl] for ikl in IL_IKL[i, l])
        >= gpy.quicksum(z[ilm] for ilm in IL_ILM[i, l])
        for (i, l) in IL
    )

    model.addConstrs(
        gpy.quicksum(z[ilm] for ilm in IM_ILM[i,m]) >= d[i, m]
        for (i, m) in IM
    )

    model.update()

    if solve:
        model.Params.OutputFlag = 0
        model.Params.TimeLimit = 0
        model.optimize()
