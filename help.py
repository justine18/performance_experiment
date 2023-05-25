import pandas as pd
import os
import json


def incremental_range(start, stop, step, inc):
    value = start
    while value < stop:
        yield value
        value += step
        step += inc


def create_data_frame():
    return pd.DataFrame(
        {"I": [], "Language": [], "MeanTime": [], "MedianTime": [], "MinTime": []}
    )


def save_to_json(symbol, name, i, model):
    if not os.path.exists(os.path.join(model, "data")):
        os.makedirs(os.path.join(model, "data"))
    file = os.path.join(model, "data", f"data_{name}{i}.json")
    with open(file, "w") as f:
        json.dump(symbol, f)


def save_to_json_d(df, name, i, model):
    if not os.path.exists(os.path.join(model, "data")):
        os.makedirs(os.path.join(model, "data"))
    file = os.path.join(model, "data", f"data_{name}{i}.json")
    df[["i", "m", "value"]].to_json(file, orient="values")


def below_time_limit(df, limit):
    return (df["MinTime"].max() < limit) or (df.empty)


def process_results(r, res_df):
    return pd.concat([res_df, r])


def print_log_message(language, n, df):
    # define a standardized log
    log = "{language:<17} done {n:>6} in {time:>}s"
    print(
        (
            log.format(
                language=language,
                n=n,
                time=round(df["MinTime"].max(), 2),
            )
        )
    )


def save_results(df, solve, model):
    if not os.path.exists(os.path.join(model, "results")):
        os.makedirs(os.path.join(model, "results"))
    file = (
        os.path.join(model, "results", "experiment_results_solve.csv")
        if solve
        else os.path.join(model, "results", "experiment_results_model.csv")
    )
    df.pivot(index="I", columns="Language", values="MinTime").to_csv(file)
