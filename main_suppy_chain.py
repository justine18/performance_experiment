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
from supply_chain.run_gurobipy import run_intuitive_gurobi, run_gurobi
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
    df_intuitive_gurobi = create_data_frame()
    df_gurobi = create_data_frame()

    # define the x axis
    N = list(incremental_range(50, cardinality_of_i + 1, 20, 10))

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
            ik_tuple,
            il_tuple,
            im_tuple,
            ijk_tuple,
            ikl_tuple,
            ilm_tuple,
            d_dict,
        ) = data.create_variable_data(n=n, J=J, K=K, L=L, M=M)
        # make dictionaries
        IK_IJK, IK_IKL, IL_IKL, IL_ILM, IM_ILM = data.data_to_dicts(
            ik_tuple, il_tuple, im_tuple, ijk_tuple, ikl_tuple, ilm_tuple
        )

        # save data to json for JuMP
        save_to_json(ik_tuple, "IK", f"_{n}", "supply_chain")
        save_to_json(il_tuple, "IL", f"_{n}", "supply_chain")
        save_to_json(im_tuple, "IM", f"_{n}", "supply_chain")
        save_to_json(ijk_tuple, "IJK", f"_{n}", "supply_chain")
        save_to_json(ikl_tuple, "IKL", f"_{n}", "supply_chain")
        save_to_json(ilm_tuple, "ILM", f"_{n}", "supply_chain")
        save_to_json_d(d_dict, "D", f"_{n}", "supply_chain")

        # Intuitive GurobiPy
        if below_time_limit(df_intuitive_gurobi, time_limit):
            rr = run_intuitive_gurobi(
                I=I,
                ik=ik_tuple,
                il=il_tuple,
                im=im_tuple,
                ijk=ijk_tuple,
                ikl=ikl_tuple,
                ilm=ilm_tuple,
                D=d_dict,
                solve=solve,
                repeats=repeats,
                number=number,
            )
            df_intuitive_gurobi = process_results(rr, df_intuitive_gurobi)
            print_log_message(
                language="Intuitive GurobiPy", n=n, df=df_intuitive_gurobi
            )

        # GurobiPy
        if below_time_limit(df_gurobi, time_limit):
            rr = run_gurobi(
                I=I,
                ik=ik_tuple,
                il=il_tuple,
                im=im_tuple,
                ijk=ijk_tuple,
                ikl=ikl_tuple,
                ilm=ilm_tuple,
                ik_ijk=IK_IJK,
                ik_ikl=IK_IKL,
                il_ikl=IL_IKL,
                il_ilm=IL_ILM,
                im_ilm=IM_ILM,
                D=d_dict,
                solve=solve,
                repeats=repeats,
                number=number,
            )
            df_gurobi = process_results(rr, df_gurobi)
            print_log_message(language="GurobiPy", n=n, df=df_gurobi)

        # Intuitive Pyomo
        if below_time_limit(df_intuitive_pyomo, time_limit):
            rr = run_intuitive_pyomo(
                I=I,
                IK=ik_tuple,
                IL=il_tuple,
                IM=im_tuple,
                IJK=ijk_tuple,
                IKL=ikl_tuple,
                ILM=ilm_tuple,
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
                IK=ik_tuple,
                IL=il_tuple,
                IM=im_tuple,
                IJK=ijk_tuple,
                IKL=ikl_tuple,
                ILM=ilm_tuple,
                IK_IJK=IK_IJK,
                IK_IKL=IK_IKL,
                IL_IKL=IL_IKL,
                IL_ILM=IL_ILM,
                IM_ILM=IM_ILM,
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
            df_intuitive_gurobi,
            df_gurobi,
        ]
    ).reset_index(drop=True)

    # save results
    save_results(df, solve, "supply_chain")

    # plot results
    visualization.plot_results(df, cardinality_of_j, solve, "supply_chain")


if __name__ == "__main__":
    CI = 8000
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
