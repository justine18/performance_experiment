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
    return J, K, L, M


def create_variable_data(n, J, K, L, M):
    I = [f"i{x}" for x in range(1, n + 1)]

    share = int(np.ceil(len(J) * 0.05))

    # IJ
    IJ = set()
    # draw a set of units j able to process product i
    IJ = set([(i, j) for i in I for j in random.sample(J, share)])
    # make sure that every unit j is able to process at least one product i
    used_j = set([j for i, j in IJ])
    for j in J:
        if not j in used_j:
            IJ.add((random.choice(I), j))

    # JK
    JK = set([(j, k) for j in J for k in random.sample(K, share)])
    # make sure that every unit j is able to process at least one product i
    used_k = set([k for j, k in JK])
    for k in K:
        if not k in used_k:
            JK.add((random.choice(J), k))

    # IK
    df_IJ = pd.DataFrame(IJ, columns=["i", "j"])
    df_JK = pd.DataFrame(JK, columns=["j", "k"])
    df_IJK = df_IJ.merge(right=df_JK, how="inner")
    IJK = df_IJK.values.tolist()
    # reduce IJK by around 50%
    reduced_IJK = random.sample(IJK, int(np.ceil(len(IJK) * 0.5)))
    IK = set([(i, k) for i, j, k in reduced_IJK])

    # KL & LM
    KL = set()
    LM = set()
    for k in K:
        for m in M:
            ll = random.sample(L, share)
            for l in ll:
                KL.add((k, l))
                LM.add((l, m))
    # does every l has a k
    used_l = set([l for k, l in KL])
    for l in L:
        if not l in used_l:
            KL.add((random.choice(K), l))
    # does every l has an m
    used_l = set([l for l, m in LM])
    for l in L:
        if not l in used_l:
            LM.add((l, random.choice(M)))

    # IL, IM
    df_KL = pd.DataFrame(KL, columns=["k", "l"])
    df_LM = pd.DataFrame(LM, columns=["l", "m"])
    df_IJKLM = df_IJK.merge(right=df_KL, how="inner").merge(right=df_LM, how="inner")
    IJKLM = df_IJKLM.values.tolist()
    IL = set([(i, l) for i, j, k, l, m in IJKLM])
    IM = set([(i, m) for i, j, k, l, m in IJKLM])

    # Demand
    D = {(i, m): random.randint(0, 100) for i, m in IM}

    return I, IJ, IK, JK, KL, LM, D
