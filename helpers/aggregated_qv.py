import numpy as np, ast, networkx as nx, matplotlib.pyplot as plt

QV_THRESHOLD = 2 / 3
Z_97 = 1.88  # one-sided 97% z-value

def node_scores_from_subsets(df):
    node_vals = {}
    node_errs = {}

    for _, row in df.iterrows():
        subset = ast.literal_eval(row["subset"])
        score = float(row["mean_HOP"])
        err = float(row["hop_error"])

        for node in subset:
            node_vals.setdefault(node, []).append(score)
            node_errs.setdefault(node, []).append(err)

    score = {}
    error = {}

    for n in node_vals:
        vals = np.array(node_vals[n], dtype=float)
        errs = np.array(node_errs[n], dtype=float)
        k = len(vals)

        score[n] = float(np.mean(vals))
        error[n] = float(np.sqrt(np.sum(errs**2)) / k)

    return score, error


def compute_node_margin(G, df, z_97=Z_97, qv_threshold=QV_THRESHOLD):
    score, error = node_scores_from_subsets(df)

    nodes = list(G.nodes())
    vals = np.array([score.get(n, np.nan) for n in nodes], dtype=float)
    errs = np.array([error.get(n, 0.0) for n in nodes], dtype=float)

    lower_bound = vals - z_97 * errs
    margin = lower_bound - qv_threshold

    return nodes, margin


def plot_aggregated_qv_grid(G, pos, dfs_by_q, z_97=Z_97, qv_threshold=QV_THRESHOLD):
    plt.rcParams.update({
        "font.size": 18,
        "axes.titlesize": 22,
        "axes.labelsize": 20,
        "xtick.labelsize": 16,
        "ytick.labelsize": 16,
    })

    margins_by_q = {}

    for q, df in dfs_by_q.items():
        nodes, margin = compute_node_margin(G, df, z_97, qv_threshold)
        margins_by_q[q] = (nodes, margin)

    # shared color scale
    all_margins = np.concatenate([
        m[1][~np.isnan(m[1])] for m in margins_by_q.values()
    ])
    vmax = np.max(np.abs(all_margins))
    norm = plt.Normalize(vmin=-vmax, vmax=vmax)
    cmap = plt.cm.coolwarm

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
        nodes, margin = margins_by_q[q]
        colors = cmap(norm(margin))

        nx.draw(
            G,
            pos,
            ax=ax,
            node_color=colors,
            with_labels=True,
            node_size=550,
            width=1.5,
            font_size=9,
        )

        ax.set_title(f"{q}-qubit subsets", fontsize=22)
        ax.set_axis_off()

    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = fig.colorbar(sm, cax=cax)
    cbar.set_label("Aggregated QV margin (lower bound − 2/3)", fontsize=20)
    cbar.ax.tick_params(labelsize=16)

    fig.savefig("results/aggregated_qv_grid.pdf", bbox_inches="tight")
    plt.show()
    plt.close(fig)
    
