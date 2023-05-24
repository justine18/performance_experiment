import pandas as pd
import numpy as np
import random

random.seed(13)


########## Data ##########
def create_fixed_data(m):
    J = [f"j{x}" for x in range(1, m + 1)]
    K = [f"k{x}" for x in range(1, m + 1)]
    L = [f"l{x}" for x in range(1, m + 1)]
    M = [f"m{x}" for x in range(1, m + 1)]

    JK = pd.DataFrame(
        np.random.binomial(1, 0.05, size=(len(J) * len(K))),
        index=pd.MultiIndex.from_product([J, K], names=["j", "k"]),
        columns=["value"],
    ).reset_index()
    KL = pd.DataFrame(
        np.random.binomial(1, 0.05, size=(len(K) * len(L))),
        index=pd.MultiIndex.from_product([K, L], names=["k", "l"]),
        columns=["value"],
    ).reset_index()
    lm = {m: random.choice(L) for m in M}
    LM_dict = {"l": [], "m": [], "value": []}
    for m in M:
        for l in L:
            LM_dict["m"].append(m)
            LM_dict["l"].append(l)
            if l in lm[m]:
                LM_dict["value"].append(1)
            else:
                LM_dict["value"].append(0)
    LM = pd.DataFrame(LM_dict)
    return J, K, L, M, JK, KL, LM


def create_variable_data(n, J, K, M, LM):
    I = [f"i{x}" for x in range(1, n + 1)]

    IJ = pd.DataFrame(
        np.random.binomial(1, 0.05, size=(len(I) * len(J))),
        index=pd.MultiIndex.from_product([I, J], names=["i", "j"]),
        columns=["value"],
    ).reset_index()
    IK = pd.DataFrame(
        np.random.binomial(1, 0.05, size=(len(I) * len(K))),
        index=pd.MultiIndex.from_product([I, K], names=["i", "k"]),
        columns=["value"],
    ).reset_index()
    D = pd.DataFrame(
        np.random.randint(0, 100, size=(len(I) * len(M))),
        index=pd.MultiIndex.from_product([I, M], names=["i", "m"]),
        columns=["value"],
    ).reset_index()

    return I, IJ, IK, D


def validate_variable_data_and_convert_to_tuples(IJ, JK, IK, KL, D):
    # check if there is at least one x variable
    if (
        IK[IK["value"] == 1]
        .merge(right=IJ[IJ["value"] == 1])
        .merge(right=JK[JK["value"] == 1])
        .empty
    ):
        index = JK[JK["value"] == 1].index[0]
        j = JK.iloc[index]["j"]
        k = JK.iloc[index]["k"]
        IJ.at[IJ.loc[(IJ["i"] == "i1") & (IJ["j"] == j)].index[0], "value"] = 1
        IK.at[IK.loc[(IK["i"] == "i1") & (IK["k"] == k)].index[0], "value"] = 1
    
    # check if there is at least one y variable
    if IK[IK["value"] == 1].merge(right=KL[KL["value"] == 1]).empty:
        index = KL[KL["value"] == 1].index[0]
        k = KL.iloc[index]["k"]
        IK.at[IK.loc[(IK["i"] == "i1") & (IK["k"] == k)].index[0], "value"] = 1
    
    # convert to tuples
    ij = [
        tuple(x) for x in IJ.loc[IJ["value"] == 1][["i", "j"]].to_dict("split")["data"]
    ]
    ik = [
        tuple(x) for x in IK.loc[IK["value"] == 1][["i", "k"]].to_dict("split")["data"]
    ]
    d = {(i, m): v for (i, m, v) in D[["i", "m", "value"]].to_dict("split")["data"]}

    return IJ, IK, ij, ik, d

def fixed_data_to_tuples(JK, KL, LM):
    jk = [
        tuple(x) for x in JK.loc[JK["value"] == 1][["j", "k"]].to_dict("split")["data"]
    ]
    kl = [
        tuple(x) for x in KL.loc[KL["value"] == 1][["k", "l"]].to_dict("split")["data"]
    ]
    lm = [
        tuple(x) for x in LM.loc[LM["value"] == 1][["l", "m"]].to_dict("split")["data"]
    ]
    return jk, kl, lm