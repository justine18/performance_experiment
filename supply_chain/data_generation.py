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

    IJ = []
    IK = []
    JK = []
    KL = []
    LM = []
    d = {(i, m): 0 for i in I for m in M}

    share = int(np.ceil(len(J) * 0.05))

    for i in I:
        jj = random.sample(J, k=share)
        for j in jj:
            kk = random.sample(K, k=share)
            for k in kk:
                IK.append((i, k))
                IJ.append((i, j))
                JK.append((j, k))

                ll = random.sample(L, k=share)
                for l in ll:
                    KL.append((k, l))
                    for m in M:
                        ll = random.sample
                        LM.append((l, m))
                        d[(i, m)] = random.randint(0, 100)
    return I, IJ, IK, JK, KL, LM, d
