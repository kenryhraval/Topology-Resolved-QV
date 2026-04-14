import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def load_calibration_csv(path):
    df = pd.read_csv(path)

    df = df.rename(columns={
        "Qubit": "node",
        "T1 (us)": "T1",
        "T2 (us)": "T2",
        "Readout assignment error": "readout_error",
        "RX error": "x_error",
        "√x (sx) error": "sx_error",
        "Pauli-X error": "pauli_x_error",
        "ID error": "id_error",
        "MEASURE error": "measure_error",
        "Readout length (ns)": "readout_length",
        "Single-qubit gate length (ns)": "single_qubit_gate_length",
        "Z-axis rotation (rz) error": "rz_error",
        "Operational": "operational",
    })

    keep_cols = [
        "node",
        "T1",
        "T2",
            # "readout_error",
        "Prob meas0 prep1",
        "Prob meas1 prep0",
        "readout_length",
        "id_error",
        "single_qubit_gate_length",
        "x_error",
        "rz_error",
        "sx_error",
        "pauli_x_error",
        "measure_error",
        "operational",
    ]

    existing_keep_cols = [c for c in keep_cols if c in df.columns]
    df = df[existing_keep_cols].copy()

    return df


def plot_node_metric_correlations(
    node_metrics_csv="results/all_node_metrics.csv",
    y_col="mean_score",
):
    df_all = pd.read_csv(node_metrics_csv)

    x_cols = [
        "T1",
        "T2",
            # "readout_error",
        "Prob meas0 prep1",
        "Prob meas1 prep0",
        "id_error",
        "x_error",
        "sx_error",
        "pauli_x_error",
        "measure_error",
    ]

    pretty_names = {
        # "readout_error": "Readout error",
        "x_error": "$X$ error",
        "sx_error": "$\\sqrt{X}$ error",
        "pauli_x_error": "Pauli-$X$ error",
        "id_error": "ID error",
        "measure_error": "Measure error",
        "T1": "$T_1$ ($\\mu$s)",
        "T2": "$T_2$ ($\\mu$s)",
        "Prob meas0 prep1": "Meas0 prep1",
        "Prob meas1 prep0": "Meas1 prep0",
    }

    x_cols = [c for c in x_cols if c in df_all.columns]

    for q in sorted(df_all["q"].dropna().unique()):
        sub = df_all[df_all["q"] == q]

        ncols = len(x_cols)

        fig, axes = plt.subplots(
            1,
            ncols,
            figsize=(4 * ncols, 4),
            constrained_layout=True,
        )

        if ncols == 1:
            axes = [axes]

        for j, xcol in enumerate(x_cols):
            ax = axes[j]

            plot_df = sub[[xcol, y_col]].dropna()

            if plot_df.empty:
                ax.set_title(f"{pretty_names.get(xcol, xcol)}\nno data")
                ax.set_xlabel(pretty_names.get(xcol, xcol))
                ax.set_ylabel(y_col)
                continue

            x = plot_df[xcol].to_numpy()
            y = plot_df[y_col].to_numpy()

            ax.scatter(x, y)

            if len(plot_df) >= 2 and np.unique(x).size > 1 and np.unique(y).size > 1:
                r = np.corrcoef(x, y)[0, 1]
                ax.set_title(f"{pretty_names.get(xcol, xcol)}\nr = {r:.2f}")
            else:
                ax.set_title(f"{pretty_names.get(xcol, xcol)}\nconstant")

            ax.set_xlabel(pretty_names.get(xcol, xcol))
            ax.set_ylabel(y_col)

        fig.savefig(f"results/node_metric_correlations_q{q}.pdf", bbox_inches="tight")
        plt.close(fig)
        

def build_correlation_table_latex(
    node_metrics_csv="results/all_node_metrics.csv",
    out_path="results/correlation_table.tex",
    y_col="mean_score",
):
    df_all = pd.read_csv(node_metrics_csv)

    x_cols = [
        "T1",
        "T2",
            # "readout_error",
        "Prob meas0 prep1",
        "Prob meas1 prep0",
        "id_error",
        "x_error",
        "sx_error",
        "pauli_x_error",
        "measure_error",
    ]

    # only keep cols that actually exist
    x_cols = [c for c in x_cols if c in df_all.columns]

    data = {}

    for x in x_cols:
        row = {}

        for q in sorted(df_all["q"].dropna().unique()):
            sub = df_all[df_all["q"] == q]
            df = sub[[x, y_col]].dropna()

            if len(df) >= 2 and df[x].nunique() > 1 and df[y_col].nunique() > 1:
                r = np.corrcoef(df[x], df[y_col])[0, 1]
                row[q] = f"{r:.2f}"
            else:
                row[q] = ""

        data[x] = row

    table = pd.DataFrame(data).T

    pretty_names = {
        # "readout_error": "Readout error",
        "x_error": "$X$ error",
        "sx_error": "$\\sqrt{X}$ error",
        "pauli_x_error": "Pauli-$X$ error",
        "id_error": "ID error",
        "measure_error": "Measure error",
        "T1": "$T_1$ ($\\mu$s)",
        "T2": "$T_2$ ($\\mu$s)",
        "Prob meas0 prep1": "Meas0 prep1",
        "Prob meas1 prep0": "Meas1 prep0",
    }

    table = table.rename(index=lambda x: pretty_names.get(x, x.replace("_", " ")))

    latex_str = table.to_latex(
        escape=False,
        bold_rows=True,
    )

    with open(out_path, "w") as f:
        f.write(latex_str)

