import ast
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx


def best_worst_subsets(df, k=1):
    df_sorted = df.sort_values("mean_HOP", ascending=False).reset_index(drop=True)

    best = df_sorted.head(k).copy()
    worst = df_sorted.tail(k).copy().sort_values("mean_HOP", ascending=True).reset_index(drop=True)

    best["subset"] = best["subset"].apply(ast.literal_eval)
    worst["subset"] = worst["subset"].apply(ast.literal_eval)

    return best, worst


def draw_best_worst_overlay(ax, G, pos, best, worst):
    norm = plt.Normalize(vmin=0.5, vmax=0.875)
    best_cmap = plt.cm.Greens
    worst_cmap = plt.cm.Reds

    nx.draw(
        G,
        pos,
        ax=ax,
        node_color="#d9d9d9",
        edge_color="#bfbfbf",
        with_labels=True,
        node_size=350,
        width=0.8,
        font_size=9,
    )

    for i in range(len(worst)):
        subset = set(worst.iloc[i]["subset"])
        hop = float(worst.iloc[i]["mean_HOP"])
        color = worst_cmap(norm(hop))

        nx.draw_networkx_nodes(
            G, pos,
            nodelist=list(subset),
            node_color=[color],
            node_size=360,
            ax=ax,
            alpha=0.9,
        )

        nx.draw_networkx_edges(
            G, pos,
            edgelist=[(u, v) for u, v in G.edges() if u in subset and v in subset],
            edge_color=[color],
            width=2.5,
            ax=ax,
        )

    for i in range(len(best)):
        subset = set(best.iloc[i]["subset"])
        hop = float(best.iloc[i]["mean_HOP"])
        color = best_cmap(norm(hop))

        nx.draw_networkx_nodes(
            G, pos,
            nodelist=list(subset),
            node_color=[color],
            node_size=360,
            ax=ax,
            alpha=0.95,
        )

        nx.draw_networkx_edges(
            G, pos,
            edgelist=[(u, v) for u, v in G.edges() if u in subset and v in subset],
            edge_color=[color],
            width=2.5,
            ax=ax,
        )

    ax.set_axis_off()


def plot_best_worst_grid(G, pos, dfs_by_q):
    plt.rcParams.update({
        "font.size": 18,
        "axes.titlesize": 22,
        "axes.labelsize": 20,
        "xtick.labelsize": 16,
        "ytick.labelsize": 16,
    })

    fig = plt.figure(figsize=(18, 10), constrained_layout=True)
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 0.05])

    axes = [
        fig.add_subplot(gs[0, 0]),
        fig.add_subplot(gs[0, 1]),
        fig.add_subplot(gs[1, 0]),
        fig.add_subplot(gs[1, 1]),
    ]

    cax = fig.add_subplot(gs[:, 2])

    norm = plt.Normalize(vmin=0.5, vmax=0.875)
    cmap = plt.cm.coolwarm

    for ax, q in zip(axes, sorted(dfs_by_q.keys())):
        df = dfs_by_q[q]

        best, worst = best_worst_subsets(df)

        nx.draw(
            G,
            pos,
            ax=ax,
            node_color="#d9d9d9",
            edge_color="#bfbfbf",
            with_labels=True,
            node_size=550,
            width=1.2,
            font_size=9,
        )

        for i in range(len(worst)):
            subset = set(worst.iloc[i]["subset"])
            hop = float(worst.iloc[i]["mean_HOP"])
            color = cmap(norm(hop))

            nx.draw_networkx_nodes(
                G, pos,
                nodelist=list(subset),
                node_color=[color],
                node_size=580,
                ax=ax,
                alpha=0.9,
            )

            nx.draw_networkx_edges(
                G, pos,
                edgelist=[(u, v) for u, v in G.edges() if u in subset and v in subset],
                edge_color=[color],
                width=3.0,
                ax=ax,
            )

        for i in range(len(best)):
            subset = set(best.iloc[i]["subset"])
            hop = float(best.iloc[i]["mean_HOP"])
            color = cmap(norm(hop))

            nx.draw_networkx_nodes(
                G, pos,
                nodelist=list(subset),
                node_color=[color],
                node_size=580,
                ax=ax,
                alpha=0.95,
            )

            nx.draw_networkx_edges(
                G, pos,
                edgelist=[(u, v) for u, v in G.edges() if u in subset and v in subset],
                edge_color=[color],
                width=3.0,
                ax=ax,
            )

        ax.set_title(f"{q}-qubit subsets", fontsize=22)
        ax.set_axis_off()

    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = fig.colorbar(sm, cax=cax)
    cbar.set_label("Subset mean HOP", fontsize=20)
    cbar.ax.tick_params(labelsize=16)

    fig.savefig("results/best_worst_grid.pdf", bbox_inches="tight")
    plt.show()
    plt.close(fig)

    