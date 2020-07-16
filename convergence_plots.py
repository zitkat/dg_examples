"""
Functions for plotting parametrized and aggregated results of convergence
studies run using soops
"""
import pandas as pd
from pathlib import Path
from glob import glob

import numpy as nm
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.legend import Legend
from matplotlib.lines import Line2D

order_symbols = dict(zip(nm.arange(0, 6, dtype=float),
                         ["o", "d", "v", "^", "s", "p"]))

gel_names = {"1_2": "",
             "2_3": "Triangles",
             "2_4": "Quadrilaterals"}


def calculate_num_order(err_df):
    """
    Uses diff_l2 and n_rows columns of the dataframe to calculate num_order,
    splits dataframe on order column
    :param err_df: dataframe, columns: ["n_rows", "order", diff_l2]
    :return:
    """
    res_df = pd.DataFrame()
    for order in err_df["order"].unique():
        order_err_df = err_df[err_df["order"] == order].sort_values("n_cells")

        dim = int(err_df.iloc[0]["gel"][0])

        num_orders = [nm.NAN]

        last_err = order_err_df.iloc[0]["diff_l2"]
        last_h = order_err_df.iloc[0]["h"]
        #         print(order_err_df.iloc[1:, :])
        for i, row in order_err_df.iloc[1:, :].iterrows():
            num_order = nm.log(row["diff_l2"] / last_err) \
                        / nm.log(row["h"] ** dim / last_h ** dim)
            #             print(row["err_l2"] / last_err)
            #             print(row["n_rows] / last_h)
            #             print("-------------------")

            last_err = row["diff_l2"]
            last_h = row["h"]
            num_orders.append(num_order)

        order_err_df["num_order"] = num_orders
        res_df = res_df.append(order_err_df)
    return res_df


def plot_marked_var(df, mk_var, x_var, y_var, mark_symbols=None,
                    fig=None, ax=None, **kwargs):
    if mark_symbols is None:
        mark_symbols = order_symbols
    if fig is None or ax is None:
        fig, ax = plt.subplots(1, 1)

    ax.set_xscale('log', basex=2)
    ax.set_yscale('log', basey=10)
    ax.grid(True)

    kwargs = kwargs.copy()
    alpha = kwargs.pop("alpha", 1.0)
    color = kwargs.pop("color", None)

    label_ext = str(kwargs.pop("label", ""))

    mark_vals = sorted(df[mk_var].unique())
    for mk in mark_vals:
        curr_df = df[df[mk_var] == mk]
        if color is not None:
            l, = ax.plot(curr_df[x_var], curr_df[y_var],
                         mark_symbols[mk], label=str(int(mk)) + label_ext,
                         color=color,
                         **kwargs)
        else:
            l, = ax.plot(curr_df[x_var], curr_df[y_var],
                         mark_symbols[mk], label=str(int(mk)) + label_ext,
                         **kwargs)

        ax.plot(curr_df[x_var], curr_df[y_var], label="",
                alpha=alpha, color=l.get_color(),
                **kwargs)

        # for i, r in curr_df.loc[~curr_df["num_order"].isnull(), :].iterrows():
        #     ax.text(r[x_var], r["diff_l2"], "{:.2f}".format(r["num_order"]))

    omarks = [Line2D([0], [0], marker=mark_symbols[o], color="grey")
              for o in mark_vals]
    return omarks


def plot_parametrized_var(df,
                          x_var, y_var,
                          column_var,
                          row_var,
                          color_var,
                          mk_var="order",
                          **kwargs):
    columns = df[column_var].unique()
    rows = df[row_var].unique()
    color_vals = df[color_var].unique()
    cm = kwargs.pop("color_map", plt.cm.viridis)
    colors = cm(nm.linspace(0, 1, len(color_vals)))[::-1]

    ncol = len(columns)
    nrow = len(rows)

    y_lab = kwargs.pop("y_lab", y_var)
    x_lab = kwargs.pop("x_lab", x_var)
    clm_lab = kwargs.pop("column_lab", column_var)
    row_lab = kwargs.pop("row_lab", row_var)
    cor_lab = kwargs.pop("color_lab", color_var)
    mk_lab = kwargs.pop("mk_lab", mk_var)

    figsize = kwargs.pop("figsize", (ncol * 4, nrow * 4))
    fig, axs = plt.subplots(nrows=len(rows), ncols=len(columns),
                            figsize=figsize)
    fig.subplots_adjust(hspace=.2, wspace=.2)

    lines_ax_rect = kwargs.pop("lines_leg_rect", [0, .07, 0.01, 0.01])
    lines_ax = fig.add_axes(lines_ax_rect)
    lines_ax.set_axis_off()
    lines_n_col = kwargs.pop("lines_ncol", 3)

    marks_ax_rect = kwargs.pop("marks_leg_rect", [0.55, .07, 0.01, 0.01])
    marks_ax = fig.add_axes(marks_ax_rect)
    marks_ax.set_axis_off()

    if nrow == 1 and ncol == 1:
        axs = [[axs]]
    elif nrow == 1:
        axs = [axs]
    elif ncol == 1:
        axs = [[ax] for ax in axs]

    for ii, row_val in enumerate(rows):
        for jj, clm_val in enumerate(columns):
            ax = axs[ii][jj]
            if jj == 0:
                ax.set_ylabel(y_lab)
            olines = []
            for cc, color_val in enumerate(color_vals):
                ax.set_title("{}: {}, {}: {}".format(row_lab, row_val,
                                                     clm_lab, clm_val))
                omarks = plot_marked_var(
                    df[(df[column_var] == clm_val) &
                       (df[row_var] == row_val) &
                       (df[color_var] == color_val)],
                    mk_var=mk_var,
                    x_var=x_var, y_var=y_var, fig=fig, ax=ax,
                    color=colors[cc], label=" {}".format(color_val), **kwargs)
                olines += [Line2D([0], [0], color=colors[cc])]

            # x1 = df[x_var].min()
            # x2 = df[x_var].max()
            # ax.plot([x1, x2], [10 ** -3 * x1 ** -2, 10 ** -3 * x2 ** -2], "r")
            # ax.plot([x1, x2], [10 ** -3 * x1 ** -3, 10 ** -3 * x2 ** -3], "r")
            # ax.plot([x1, x2], [10 ** -3 * x1 ** -4, 10 ** -3 * x2 ** -4], "r")

            if ii == len(rows) - 1:
                ax.set_xlabel(x_lab)

    marks_ax.legend(handles=omarks,
                    labels=sorted(df[mk_var].unique()),
                    title=mk_lab, ncol=len(omarks),
                    borderaxespad=0., loc="upper center")

    lines_ax.legend(handles=olines,
                    labels=["{}".format(cval) for cval in color_vals],
                    title=cor_lab, ncol=lines_n_col,
                    borderaxespad=0., loc="upper center")
    return fig


def plot_agregated_var(df, y_var, x_var, color_var,
                       xlogscale=True, ylogscale=True, **kwargs):
    figsize = kwargs.pop("figsize", (8, 6))
    fig, ax = plt.subplots(figsize=figsize)
    if xlogscale:
        ax.set_xscale('log', basex=10)
    if ylogscale:
        ax.set_yscale('log', basey=10)

    y_lab = kwargs.pop("y_lab", y_var)
    x_lab = kwargs.pop("x_lab", x_var)
    cor_lab = kwargs.pop("color_lab", color_var)

    orders = sorted(df["order"].unique())
    color_vals = df[color_var].unique()
    cm = kwargs.pop("color_map", plt.cm.viridis)
    colors = cm(nm.linspace(0, 1, len(color_vals)))[::-1]

    oline = []
    for di, col_val in enumerate(color_vals):
        order_means = df[(df[color_var] == col_val)]. \
            groupby(["expid", "order"])[[x_var, color_var, y_var]] \
            .mean().reset_index("expid")

        for i in orders:
            ax.plot(order_means.loc[i][x_var], order_means.loc[i][y_var],
                    order_symbols[i], color=colors[di], label="")

            ax.plot(order_means.loc[i][x_var], order_means.loc[i][y_var],
                    color=colors[di], label=cor_lab)
        oline += [Line2D([0], [0], color=colors[di])]

    omarks = [Line2D([0], [0], marker=order_symbols[o], color="grey")
              for o in orders]
    lb = Legend(ax, omarks, labels=orders, title="Order")
    ax.add_artist(lb)

    lb = Legend(ax, oline,
                labels=[f"{cv:.0e}" for cv in color_vals],
                title=cor_lab, borderaxespad=-figsize[0],
                loc="center right",
                ncol=1  # len(oline) // 2 if len(oline) > 4 else len(oline)
                )
    ax.add_artist(lb)

    ax.set_ylabel(y_lab)
    ax.set_xlabel(x_lab)
    ax_title = kwargs.pop("ax_title", None)
    ax.set_title(ax_title)

    return fig


if __name__ == '__main__':
    folder = Path(r"outputs/parametric/example_dg_burgers1D_hesthaven/")
    df = pd.DataFrame()
    for file in folder.glob("*.csv"):
        df = df.append(
            calculate_num_order(pd.read_csv(file).assign(
                expid=file.name.split("r")[0].replace("_", "")))
        )

    print("order:")
    print(df["order"].unique())
    print("gel:")
    print(df["gel"].unique())
    print("diffcoef:")
    print(df["diffcoef"].unique())
    print("cw:")
    print(df["cw"].unique())

    df["h-2"] = 1 / df["h"] ** 2

    f = plot_parametrized_var(df[(df["limit"] == False)],
                              y_var="diff_l2", y_lab="$L^2$ relative error",
                              x_var="h-2", x_lab="$1/h^2$",
                              row_var="diffcoef", row_lab="Diffusion $D$",
                              column_var="limit", column_lab="Limiting",
                              color_var="cw",
                              color_lab="Penalty coefficient $C_w$",
                              alpha=.5
                              )

    f.savefig("conv_plot.pdf")

    fe = plot_agregated_var(df[(df["limit"] == False)],
                            y_var="num_order", y_lab="Order", ylogscale=False,
                            x_var="diffcoef", x_lab="Diffusion coefficient $D$",
                            color_var="cw",
                            color_lab="Penalty coefficient $C_w$")
    fe.savefig("nls_err_plot.pdf")
    plt.show()
