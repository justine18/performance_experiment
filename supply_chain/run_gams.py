import gams.transfer as gt
import subprocess
import pandas as pd
import numpy as np


########## GAMS ##########
def data_to_gams(I, J, K, L, M, IJ, JK, IK, KL, LM, D):
    c = gt.Container()

    # create sets
    i = c.addSet("i", records=I)
    j = c.addSet("j", records=J)
    k = c.addSet("k", records=K)
    l = c.addSet("l", records=L)
    m = c.addSet("m", records=M)

    c.addSet("IJ", [i, j], records=IJ[IJ["value"] == 1])
    c.addSet("JK", [j, k], records=JK[JK["value"] == 1])
    c.addSet("IK", [i, k], records=IK[IK["value"] == 1])
    c.addSet("KL", [k, l], records=KL[KL["value"] == 1])
    c.addSet("LM", [l, m], records=LM[LM["value"] == 1])

    # create parameter
    c.addParameter("time")
    c.addParameter("d", [i, m], records=D)

    # create variables
    c.addVariable("f")
    c.addVariable("x", domain=[i, j, k])
    c.addVariable("y", domain=[i, k, l])
    c.addVariable("z", domain=[i, l, m])

    c.write("supply_chain/data/data.gdx")


def run_gams(solve, N, repeats, number):
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
