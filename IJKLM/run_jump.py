import subprocess
import json
import pandas as pd
import os


########## JuMP ##########
def run_julia(solve, repeats, number, time_limit):
    subprocess.call(
        f"julia IJKLM/IJKLM.jl {solve} {repeats} {number} {time_limit}"
    )
    print("\nJulia done")

    file = (
        os.path.join("IJKLM", "results", "fast_jump_results_solve.json")
        if solve
        else os.path.join("IJKLM", "results", "fast_jump_results_model.json")
    )
    file2 = (
        os.path.join("IJKLM", "results", "jump_results_solve.json")
        if solve
        else os.path.join("IJKLM", "results", "jump_results_model.json")
    )

    with open(file, "r") as f:
        df = pd.DataFrame(json.load(f))

    with open(file2, "r") as f:
        df2 = pd.DataFrame(json.load(f))
    return df, df2
