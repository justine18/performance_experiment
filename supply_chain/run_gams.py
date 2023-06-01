import gams.transfer as gt
import subprocess
import pandas as pd
import numpy as np


########## GAMS ##########
def data_to_gams(I, J, K, L, M, IK, IL, IM, IJK, IKL, ILM, D):
    c = gt.Container()

    # create sets
    i = c.addSet("i", records=I)
    j = c.addSet("j", records=J)
    k = c.addSet("k", records=K)
    l = c.addSet("l", records=L)
    m = c.addSet("m", records=M)

    c.addSet("IK", [i, k], records=IK)
    c.addSet("IL", [i, l], records=IL)
    c.addSet("IM", [i, m], records=IM)
    c.addSet("IJK", [i, j, k], records=IJK)
    c.addSet("IKL", [i, k, l], records=IKL)
    c.addSet("ILM", [i, l, m], records=ILM)

    # create parameter
    c.addParameter("time")
    df_d = pd.DataFrame([(i, m, D[i, m]) for i, m in IM], columns=["i", "m", "value"])
    c.addParameter("d", [i, m], records=df_d)

    # create variables
    c.addVariable("f")
    c.addVariable("x", domain=[i, j, k])
    c.addVariable("y", domain=[i, k, l])
    c.addVariable("z", domain=[i, l, m])

    c.write("supply_chain/data/data.gdx")


def run_gams(I, J, K, L, M, IK, IL, IM, IJK, IKL, ILM, D, solve, N, repeats, number):
    data_to_gams(
        I=I, J=J, K=K, L=L, M=M, IK=IK, IL=IL, IM=IM, IJK=IJK, IKL=IKL, ILM=ILM, D=D
    )

    if solve:
        subprocess.call(
            f"gams supply_chain/supply_chain.gms --solve={solve} --R={repeats} --N={number}",
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )
    else:
        subprocess.call(
            f"gams supply_chain/supply_chain.gms --R={repeats} --N={number}",
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )

    c = gt.Container()
    c.read("supply_chain/results/result.gdx")
    r = c["t"].records["value"]

    result = pd.DataFrame(
        {
            "I": [N],
            "Language": ["GAMS"],
            "MinTime": [np.min(r)],
            "MeanTime": [np.mean(r)],
            "MedianTime": [np.median(r)],
        }
    )

    return result
