import pandas as pd
import numpy as np

# import submodules
import supply_chain.data_generation as data
import visualization
from help import (
    create_directories,
    create_data_frame,
    incremental_range,
    save_to_json,
    save_to_json_d,
    below_time_limit,
    process_results,
    print_log_message,
    save_results,
)
from supply_chain.run_pyomo import run_intuitive_pyomo, run_pyomo
from supply_chain.run_jump import run_julia


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
    J, K, L, M = data.create_fixed_data(m=cardinality_of_j)

    # save data to json for JuMP
    save_to_json(N, "N", "", "supply_chain")
    save_to_json(L, "L", "", "supply_chain")
    save_to_json(M, "M", "", "supply_chain")

    # run experiment for every n in |I|
    for n in N:
        # create variable data and convert to tuples
        (
            I,
            ij_tuple,
            ik_tuple,
            jk_tuple,
            kl_tuple,
            lm_tuple,
            d_dict,
        ) = data.create_variable_data(n=n, J=J, K=K, L=L, M=M)

        # save data to json for JuMP
        save_to_json(ij_tuple, "IJ", f"_{n}", "supply_chain")
        save_to_json(ik_tuple, "IK", f"_{n}", "supply_chain")
        save_to_json(kl_tuple, "KL", f"_{n}", "supply_chain")
        save_to_json(lm_tuple, "LM", f"_{n}", "supply_chain")
        save_to_json_d(d_dict, "D", f"_{n}", "supply_chain")

        # Intuitive Pyomo
        if below_time_limit(df_intuitive_pyomo, time_limit):
            rr = run_intuitive_pyomo(
                I=I,
                L=L,
                M=M,
                IJ=ij_tuple,
                JK=jk_tuple,
                IK=ik_tuple,
                KL=kl_tuple,
                LM=lm_tuple,
                D=d_dict,
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
                L=L,
                M=M,
                IJ=ij_tuple,
                JK=jk_tuple,
                IK=ik_tuple,
                KL=kl_tuple,
                LM=lm_tuple,
                D=d_dict,
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
    save_results(df, solve, "supply_chain")

    # plot results
    visualization.plot_results(df, cardinality_of_j, solve, "supply_chain")


if __name__ == "__main__":
    CI = 10000
    CJ = 20

    create_directories("supply_chain")

    for solve in [False, True]:
        run_experiment(
            cardinality_of_i=CI,
            cardinality_of_j=CJ,
            solve=solve,
            repeats=4,
            number=1,
            time_limit=5,
        )
