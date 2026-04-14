import pandas as pd, networkx as nx
from helpers.aggregated_qv import QV_THRESHOLD, Z_97
from helpers.success_fraction import compute_node_success_fraction
from helpers.aggregated_qv import compute_node_margin
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


def plot_mode_comparison_grid(G, pos, dfs_by_mode, q, z_97=Z_97, qv_threshold=QV_THRESHOLD):
    modes = ["original", "optimised"]

    margins = {}
    success_fracs = {}

    for mode in modes:
        nodes_m, margin = compute_node_margin(G, dfs_by_mode[mode], z_97, qv_threshold)
        nodes_s, frac = compute_node_success_fraction(
            G, dfs_by_mode[mode], z=z_97, threshold=qv_threshold
        )
        margins[mode] = (nodes_m, margin)
        success_fracs[mode] = (nodes_s, frac)

    all_margins = np.concatenate([
        m[1][~np.isnan(m[1])] for m in margins.values()
    ])
    vmax = np.max(np.abs(all_margins))
    margin_norm = plt.Normalize(vmin=-vmax, vmax=vmax)
    margin_cmap = plt.cm.coolwarm

    frac_norm = plt.Normalize(vmin=0.0, vmax=1.0)
    frac_cmap = plt.cm.plasma

    fig = plt.figure(figsize=(18, 10), constrained_layout=True)
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 0.05])

    axes = [
        fig.add_subplot(gs[0, 0]),
        fig.add_subplot(gs[0, 1]),
        fig.add_subplot(gs[1, 0]),
        fig.add_subplot(gs[1, 1]),
    ]

    cax_top = fig.add_subplot(gs[0, 2])
    cax_bottom = fig.add_subplot(gs[1, 2])

    for ax, mode in zip(axes[:2], modes):
        nodes, margin = margins[mode]
        colors = margin_cmap(margin_norm(margin))

        nx.draw(
            G, pos, ax=ax,
            node_color=colors,
            with_labels=True,
            node_size=350,
            width=1,
            font_size=9,
        )
        ax.set_title(f"{mode}: margin")
        ax.set_axis_off()
        ax.set_aspect("equal")

    for ax, mode in zip(axes[2:], modes):
        nodes, frac = success_fracs[mode]
        colors = frac_cmap(frac_norm(np.nan_to_num(frac, nan=0.0)))

        nx.draw(
            G, pos, ax=ax,
            node_color=colors,
            with_labels=True,
            node_size=350,
            width=1,
            font_size=9,
        )
        ax.set_title(f"{mode}: success %")
        ax.set_axis_off()
        ax.set_aspect("equal")

    sm1 = plt.cm.ScalarMappable(norm=margin_norm, cmap=margin_cmap)
    sm1.set_array([])
    fig.colorbar(sm1, cax=cax_top, label="QV margin")

    sm2 = plt.cm.ScalarMappable(norm=frac_norm, cmap=frac_cmap)
    sm2.set_array([])
    cbar2 = fig.colorbar(sm2, cax=cax_bottom, label="Successful subsets")
    cbar2.ax.yaxis.set_major_formatter(PercentFormatter(xmax=1.0))

    fig.suptitle(f"Without and with optimisation comparison for $n={q}$", fontsize=16)
    fig.savefig("results/optimisation_comparison.pdf", bbox_inches="tight")
    plt.show()
    plt.close(fig)

    