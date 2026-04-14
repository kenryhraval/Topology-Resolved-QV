import pandas as pd
import matplotlib.pyplot as plt

from helpers.aggregated_qv import Z_97

def plot_qv_summary_stats(q_values=range(3, 7), max_experiment_n=8):
    df_experiment = pd.read_csv("results/qv_until_fail.csv")
    df_stats = pd.read_csv("results/qv_summary_stats.csv")

    df_experiment = df_experiment[
        (df_experiment["n"] >= 3) &
        (df_experiment["n"] <= max_experiment_n) &
        (df_experiment["optimised"] == True)
    ].sort_values("n").copy()

    df_stats = df_stats[
        df_stats["n"].isin(q_values) &
        (df_stats["optimised"] == True)
    ].sort_values("n").copy()

    pdf = "results/qv_summary_stats.pdf"

    plt.figure(figsize=(10, 6))

    # Subset statistics: all with error bars
    plt.errorbar(
        df_stats["n"], df_stats["mean_HOP"],
        yerr=Z_97 * df_stats["mean_error"],
        marker="o", linestyle="-", capsize=4,
        label=f"Subset mean ($\\pm {Z_97}\\sigma$)"
    )
    plt.errorbar(
        df_stats["n"], df_stats["median_HOP"],
        yerr=Z_97 * df_stats["median_row_error"],
        marker="D", linestyle="--", capsize=4,
        label=f"Subset median ($\\pm {Z_97}\\sigma$)"
    )
    plt.errorbar(
        df_stats["n"], df_stats["min_HOP"],
        # yerr=Z_97 * df_stats["min_row_error"],
        marker="v", linestyle=":", capsize=4,
        label=f"Subset min"
    )
    plt.errorbar(
        df_stats["n"], df_stats["max_HOP"],
        # yerr=Z_97 * df_stats["max_row_error"],
        marker="^", linestyle=":", capsize=4,
        label=f"Subset max"
    )

    # Standard QV as filled box-like band, but only one legend label
    lower = df_experiment["mean_HOP"] - Z_97 * df_experiment["std_HOP"]
    upper = df_experiment["mean_HOP"] + Z_97 * df_experiment["std_HOP"]

    plt.fill_between(
        df_experiment["n"],
        lower,
        upper,
        alpha=0.22,
        step=None,
        label=f"Standard QV ($\\pm {Z_97}\\sigma$)"
    )

    plt.plot(
        df_experiment["n"],
        df_experiment["mean_HOP"],
        marker="s",
        linestyle="-",
        linewidth=2.5,
        label="_nolegend_"
    )

    plt.axhline(2/3, linestyle=":", linewidth=1.5, label="HOP = 2/3 threshold")

    plt.xlabel("Qubit count, n")
    plt.ylabel("Heavy output probability")
    # plt.title(r"Quantum Volume across different $n$ with error bars")
    plt.xlim(3, max_experiment_n)
    plt.ylim(0.45, 0.90)
    plt.margins(x=0)
    plt.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(pdf, bbox_inches="tight")
    plt.show()
