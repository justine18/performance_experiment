import gams.transfer as gt
import subprocess
import pandas as pd
import numpy as np


########## GAMS ##########
def data_to_gams(I, J, K, L, M, ijk, jkl, klm):
    c = gt.Container()

    # create sets
    i = c.addSet("i", records=I)
    j = c.addSet("j", records=J)
    k = c.addSet("k", records=K)
    l = c.addSet("l", records=L)
    m = c.addSet("m", records=M)

    c.addSet("IJK", [i, j, k], records=ijk[ijk["value"] == 1])
    c.addSet("JKL", [j, k, l], records=jkl[jkl["value"] == 1])
    c.addSet("KLM", [k, l, m], records=klm[klm["value"] == 1])

    # create parameter
    c.addParameter("time")

    # create variables
    c.addVariable("z")
    c.addVariable("x", domain=[i, j, k, l, m])

    c.write("IJKLM/data/data.gdx")


def run_gams(solve, N, repeats, number):
    if solve:
        subprocess.call(
            f"gams IJKLM/IJKLM.gms --R={repeats} --N={number}",
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )
    else:
        subprocess.call(
            f"gams IJKLM/IJKLM.gms --solve={solve} --R={repeats} --N={number}",
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )

    c = gt.Container()
    c.read("IJKLM/results/result.gdx")
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
