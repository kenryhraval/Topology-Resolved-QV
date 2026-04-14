import numpy as np, ast, networkx as nx, matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

from helpers.aggregated_qv import QV_THRESHOLD, Z_97

def node_qv_success_fraction(df, z=Z_97, threshold=QV_THRESHOLD):
    total = {}
    success = {}

    for _, row in df.iterrows():
        subset = ast.literal_eval(row["subset"])

        mean_hop = float(row["mean_HOP"])
        hop_err = float(row["hop_error"])

        lower_bound = mean_hop - z * hop_err
        is_success = lower_bound > threshold

        for q in subset:
            total[q] = total.get(q, 0) + 1
            if is_success:
                success[q] = success.get(q, 0) + 1

    fraction = {q: success.get(q, 0) / total[q] for q in total}
    return success, total, fraction


def compute_node_success_fraction(G, df, z=Z_97, threshold=QV_THRESHOLD):
    _, _, fraction = node_qv_success_fraction(df, z=z, threshold=threshold)
    nodes = list(G.nodes())
    vals = np.array([fraction.get(n, np.nan) for n in nodes], dtype=float)
    return nodes, vals


def plot_qv_success_fraction_grid(G, pos, dfs_by_q, z_97=Z_97, qv_threshold=QV_THRESHOLD):
    fractions_by_q = {}

    for q, df in dfs_by_q.items():
        nodes, vals = compute_node_success_fraction(G, df, z=z_97, threshold=qv_threshold)
        fractions_by_q[q] = (nodes, vals)

    norm = plt.Normalize(vmin=0.0, vmax=1.0)
    cmap = plt.cm.plasma

    fig = plt.figure(figsize=(18, 10), constrained_layout=True)
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 0.05])

    axes = [
        fig.add_subplot(gs[0, 0]),
        fig.add_subplot(gs[0, 1]),
        fig.add_subplot(gs[1, 0]),
        fig.add_subplot(gs[1, 1]),
    ]
    cax = fig.add_subplot(gs[:, 2])

    for ax, q in zip(axes, sorted(dfs_by_q.keys())):
        nodes, vals = fractions_by_q[q]
        colors = cmap(norm(np.nan_to_num(vals, nan=0.0)))

        nx.draw(
            G,
            pos,
            ax=ax,
            node_color=colors,
            with_labels=True,
            node_size=350,
            width=1,
            font_size=9,
        )

        ax.set_title(f"{q}-qubit subsets")
        ax.set_axis_off()

    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = fig.colorbar(sm, cax=cax, label="Successful subsets (lower bound > 2/3)")
    cbar.ax.yaxis.set_major_formatter(PercentFormatter(xmax=1.0))

    # plt.title(r"Qubit QV success fraction across subset sizes $n$")

    plt.show()

    fig.savefig("results/success_fraction_grid.pdf", bbox_inches="tight")
    plt.close(fig)

