import timeit
import xarray as xr
import pandas as pd
import numpy as np
import linopy
from contextlib import redirect_stdout, redirect_stderr
import os


########## Linopy ##########
def run_linopy(I, ijk_tuple, jkl_tuple, klm_tuple, solve, repeats, number):
    # convert sets to dataframes
    IJK = pd.DataFrame(ijk_tuple, columns=list("ijk"))
    JKL = pd.DataFrame(jkl_tuple, columns=list("jkl"))
    KLM = pd.DataFrame(klm_tuple, columns=list("klm"))

    setup = {
        "I": I,
        "IJK": IJK,
        "JKL": JKL,
        "KLM": KLM,
        "solve": solve,
        "model_function": fast_linopy,
    }
    r = timeit.repeat(
        "model_function(IJK, JKL, KLM, solve)",
        repeat=repeats,
        number=number,
        globals=setup,
    )

    result = pd.DataFrame(
        {
            "I": [len(I)],
            "Language": ["linopy"],
            "MinTime": [np.min(r)],
            "MeanTime": [np.mean(r)],
            "MedianTime": [np.median(r)],
        }
    )
    return result


def fast_linopy(IJK, JKL, KLM, solve):
    overlaps = pd.merge(pd.merge(IJK, JKL), KLM)
    index = pd.MultiIndex.from_frame(overlaps).rename(list("IJKLM"))

    mask = pd.Series(True, index).unstack("I", fill_value=False)
    mask = xr.DataArray(mask, dims=["JKLM", "I"])

    model = linopy.Model()

    x = model.add_variables(lower=0, mask=mask, name="x")
    z = model.add_variables(lower=0, name="z")

    model.add_objective(1 * z)

    model.add_constraints(x.sum("JKLM") >= 0, name="ei")

    if solve:
        # TODO: set time limit to zero
        with open(os.devnull, "w") as devnull, redirect_stdout(
            devnull
        ), redirect_stderr(devnull):
            model.solve()
