import pandas as pd
import numpy as np

# import submodules
import IJKLM.data_generation as data
import visualization
from help import (
    create_directories,
    create_data_frame,
    incremental_range,
    below_time_limit,
    process_results,
    print_log_message,
    save_results,
)

from IJKLM.run_pyomo import run_cartesian_pyomo, run_pyomo


############## Experiment ##########################
def run_experiment(
    cardinality_of_i, cardinality_of_j, solve, repeats, number, time_limit
):
    np.random.seed(13)

    # create empty frames for results
    df_pyomo = create_data_frame()
    df_cartesian_pyomo = create_data_frame()

    # define the x axis
    N = list(incremental_range(5, cardinality_of_i + 1, 5, 5))

    # create fixed data and convert to tuples and dicts
    J, K, L, M, JKL, KLM = data.create_fixed_data(m=cardinality_of_j)
    jkl_tuple, klm_tuple = data.fixed_data_to_tuples(JKL=JKL, KLM=KLM)

    # run experiment for every n in |I|
    for n in N:
        # create variable data and convert to tuples
        I, IJK = data.create_variable_data(n=n, j=J, k=K)
        ijk_tuple = data.variable_data_to_tuples(IJK=IJK)

        # Pyomo
        if below_time_limit(df_pyomo, time_limit):
            rr = run_pyomo(
                I=I,
                IJK=ijk_tuple,
                JKL=jkl_tuple,
                KLM=klm_tuple,
                solve=solve,
                repeats=repeats,
                number=number,
            )
            df_pyomo = process_results(rr, df_pyomo)
            print_log_message(language="Pyomo", n=n, df=df_pyomo)

        # Cartesian Pyomo
        if below_time_limit(df_cartesian_pyomo, time_limit):
            rr = run_cartesian_pyomo(
                I=I,
                J=J,
                K=K,
                L=L,
                M=M,
                IJK=ijk_tuple,
                JKL=jkl_tuple,
                KLM=klm_tuple,
                solve=solve,
                repeats=repeats,
                number=number,
            )
            df_cartesian_pyomo = process_results(rr, df_cartesian_pyomo)
            print_log_message(language="Cartesian Pyomo", n=n, df=df_cartesian_pyomo)

    # merge all results
    df = pd.concat([df_pyomo, df_cartesian_pyomo]).reset_index(drop=True)

    # save results
    save_results(df, solve, "cartesian_IJKLM")

    # plot results
    visualization.plot_results(df, cardinality_of_j, solve, "cartesian_IJKLM")


if __name__ == "__main__":
    CI = 200
    CJ = 20

    create_directories("cartesian_IJKLM")

    run_experiment(
        cardinality_of_i=CI,
        cardinality_of_j=CJ,
        solve=False,
        repeats=2,
        number=1,
        time_limit=30,
    )
