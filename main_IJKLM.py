import pandas as pd
import numpy as np

# import submodules
import IJKLM.data_generation as data
import visualization
from help import (
    create_directories,
    create_data_frame,
    incremental_range,
    save_to_json,
    below_time_limit,
    process_results,
    print_log_message,
    save_results,
)
from IJKLM.run_pyomo import run_intuitive_pyomo, run_pyomo
from IJKLM.run_jump import run_julia


############## Experiment ##########################
def run_experiment(
    cardinality_of_i, cardinality_of_j, solve, repeats, number, time_limit
):
    np.random.seed(13)

    # create empty frames for results
    df_jump = create_data_frame()
    df_intuitive_jump = create_data_frame()
    df_intuitive_pyomo = create_data_frame()
    df_pyomo = create_data_frame()

    # define the x axis
    N = list(incremental_range(100, cardinality_of_i + 1, 100, 100))

    # create fixed data and convert to tuples and dicts
    J, K, JKL, KLM = data.create_fixed_data(m=cardinality_of_j)
    jkl_tuple, klm_tuple = data.fixed_data_to_tuples(JKL, KLM)
    jkl_dict, klm_dict = data.fixed_data_to_dicts(jkl_tuple, klm_tuple)

    # save data to json for JuMP
    save_to_json(N, "N", "", "IJKLM")
    save_to_json(jkl_tuple, "JKL", "", "IJKLM")
    save_to_json(klm_tuple, "KLM", "", "IJKLM")

    # run experiment for every n in |I|
    for n in N:
        # create variable data and convert to tuples
        I, IJK = data.create_variable_data(n=n, j=J, k=K)
        ijk_tuple = data.variable_data_to_tuples(IJK)

        # save data to json for JuMP
        save_to_json(ijk_tuple, "IJK", f"_{n}", "IJKLM")

        # Intuitive Pyomo
        if below_time_limit(df_intuitive_pyomo, time_limit):
            rr = run_intuitive_pyomo(
                I=I,
                IJK=ijk_tuple,
                JKL=jkl_tuple,
                KLM=klm_tuple,
                solve=solve,
                repeats=repeats,
                number=number,
            )
            df_intuitive_pyomo = process_results(rr, df_intuitive_pyomo)
            print_log_message(language="Intuitive Pyomo", n=n, df=df_intuitive_pyomo)

        # Pyomo
        if below_time_limit(df_pyomo, time_limit):
            rr = run_pyomo(
                I=I,
                IJK=ijk_tuple,
                JKL=jkl_dict,
                KLM=klm_dict,
                solve=solve,
                repeats=repeats,
                number=number,
            )
            df_pyomo = process_results(rr, df_pyomo)
            print_log_message(language="Pyomo", n=n, df=df_pyomo)

    # JuMP
    df_jump, df_intuitive_jump = run_julia(solve, repeats, number, time_limit)

    # merge all results
    df = pd.concat(
        [
            df_jump,
            df_intuitive_jump,
            df_intuitive_pyomo,
            df_pyomo,
        ]
    ).reset_index(drop=True)

    # save results
    save_results(df, solve, "IJKLM")

    # plot results
    visualization.plot_results(df, cardinality_of_j, solve, "IJKLM")


if __name__ == "__main__":
    CI = 8000
    CJ = 20

    create_directories("IJKLM")

    for solve in [False, True]:
        run_experiment(
            cardinality_of_i=CI,
            cardinality_of_j=CJ,
            solve=solve,
            repeats=3,
            number=1,
            time_limit=5,
        )
