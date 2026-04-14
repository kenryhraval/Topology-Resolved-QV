import ast
import numpy as np
import pandas as pd

QV_THRESHOLD = 2 / 3
Z_97 = 1.88


def compute_node_metrics(dfs_by_q, out_path="results/all_node_metrics.csv"):

    all_rows = []

    for q, df in dfs_by_q.items():
        node_vals = {}
        node_errs = {}

        total = {}
        success = {}

        for _, row in df.iterrows():
            subset = ast.literal_eval(row["subset"])
            mean = float(row["mean_HOP"])
            err = float(row["hop_error"])

            lower = mean - Z_97 * err
            is_success = lower > QV_THRESHOLD

            for node in subset:
                node_vals.setdefault(node, []).append(mean)
                node_errs.setdefault(node, []).append(err)

                total[node] = total.get(node, 0) + 1
                if is_success:
                    success[node] = success.get(node, 0) + 1

        for node in sorted(node_vals):
            vals = np.array(node_vals[node])
            errs = np.array(node_errs[node])
            k = len(vals)

            mean_score = np.mean(vals)
            propagated_error = np.sqrt(np.sum(errs**2)) / k
            lower_bound = mean_score - Z_97 * propagated_error
            margin = lower_bound - QV_THRESHOLD

            n_total = total[node]
            n_success = success.get(node, 0)
            frac = n_success / n_total

            all_rows.append({
                "q": q,
                "node": node,
                "k_subsets": k,

                # aggregated
                "mean_score": mean_score,
                "propagated_error": propagated_error,
                "lower_bound": lower_bound,
                "margin": margin,

                # success fraction
                "successful_subsets": n_success,
                "total_subsets": n_total,
                "success_fraction": frac,
            })

    df_out = pd.DataFrame(all_rows)
    df_out.to_csv(out_path, index=False)
