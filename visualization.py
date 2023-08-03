import seaborn as sns
import matplotlib.pyplot as plt


def plot_results(df, cardinality_of_j, solve, model, suffix):
    # Apply the default theme
    sns.set_theme(
        style="ticks",
        rc={
            "figure.dpi": 100,
        },
    )

    if solve:
        filename = f"solve_performance_{suffix}.png"
        y_label = "Time [s]"
    else:
        filename = f"model_performance_{suffix}.png"
        y_label = f"Model Generation Time [s]"

    # Plot
    plot = sns.relplot(
        data=df, x="I", y="MinTime", hue="Language", kind="line", palette="muted"
    )

    plot.fig.suptitle(
        r"$|\mathcal{J}|, |\mathcal{K}|, |\mathcal{L}|, |\mathcal{M}| = $"
        + f"{cardinality_of_j}",
        size=15,
    )
    plot.fig.subplots_adjust(top=0.85)

    plot.set(xlabel=r"$|\mathcal{I}|$", ylabel=y_label)

    plt.savefig(f"plots/{model}/{filename}", dpi=300)
