"""Plot all zero-field slope data.

Plot η(Β//, Vg) and ΔIc(Β//, Vg).

Have data from 2x devices (both Wsc=0.9μm), 2x gate sweeps each.
"""
from collections import defaultdict
from pathlib import Path

import numpy as np
from matplotlib import colormaps
from matplotlib import pyplot as plt
from matplotlib.colors import CenteredNorm, LinearSegmentedColormap
from pandas import read_csv

GATELABEL = r"$V_\mathrm{g}$ (V)"

plt.style.use(["paper", "fullcolumn"])
cpts = [  # RGB
    (103, 6, 7),
    (180, 12, 13),  # tab:red
    (255, 255, 255),  # white
    (4, 88, 147),  # tab:blue
    (1, 42, 70),
]
cpts = [(r / 255, g / 255, b / 255) for r, g, b in cpts]
cdict = defaultdict(list)
for i, c in enumerate(cpts):
    cdict["red"].append((i / (len(cpts) - 1), c[0], c[0]))
    cdict["green"].append((i / (len(cpts) - 1), c[1], c[1]))
    cdict["blue"].append((i / (len(cpts) - 1), c[2], c[2]))
cmap = LinearSegmentedColormap("custom", cdict)
colormaps.register(cmap=cmap)

outdir = Path(__file__).parent
outdir.mkdir(exist_ok=True)

device = {"NNE": "A", "ENE": "B"}

dataset_dirs = (
    "JS633-W2_Wsc=0.9um-ENE_WFS06_slopes",
    "JS633-W2_Wsc=0.9um-ENE_WFS06_slopes+10Vreset",
    "JS633-W2_Wsc=0.9um-NNE_WFS06_slopes",
    "JS633-W2_Wsc=0.9um-NNE_WFS07_slopes",
)
datapaths = [
    Path(f"../../data/processed/centermax/{dir_}/data_deduped.csv")
    for dir_ in dataset_dirs
]
slopepaths = [
    Path(f"../../data/processed/centermax/{dir_}/slopes_deduped.csv")
    for dir_ in dataset_dirs
]


def subtract_zerofield_offsets(df):
    """Subtract η(B∥=0) from η(B∥) (likewise for ΔIc).

    `df` should contain a single Vg value.
    For use with pandas groupby(Vg).apply().
    """
    (zoffset,) = df["eta"][df["field"] == 0].values  # should only be 1
    df["eta"] -= zoffset
    (zoffset,) = df["delta"][df["field"] == 0].values  # should only be 1
    df["delta"] -= zoffset
    return df


for path in datapaths:
    # η
    fig1, axs1 = plt.subplots(ncols=3, sharey=True, figsize=(8.5 - 1.5, 3))
    # ΔIc
    fig2, axs2 = plt.subplots(ncols=3, sharey=True, figsize=(8.5 - 1.5, 3))
    for ax in (axs1[0], axs2[0]):
        ax.set_ylabel(GATELABEL)

    outsubdir = outdir / path.parent.name
    outsubdir.mkdir(exist_ok=True)

    df = read_csv(path)
    df.sort_values(by=["field", "gate"], inplace=True)
    df.drop(df[df["gate"] < -6.5].index, inplace=True)
    df["delta_mean"] = df.groupby("gate")["delta"].transform(lambda s: s.mean())
    df["eta_mean"] = df.groupby("gate")["eta"].transform(lambda s: s.mean())
    df["delta_mean_err"] = df.groupby("gate")["delta_err"].transform(
        lambda s: np.sqrt((s**2).sum()) / s.size
    )
    df["eta_mean_err"] = df.groupby("gate")["eta_err"].transform(
        lambda s: np.sqrt((s**2).sum()) / s.size
    )

    # plot zero-field offsets (means)
    df0 = df[df["field"] == 0]
    for xcol, xlabel, xunit, ax in zip(
        ("eta_mean", "delta_mean"),
        (
            r"$\overline{\eta}$ (%)",
            r"$\overline{\Delta I_\mathrm{c}}$ (nA)",
        ),
        (1 / 100, 1e-9),
        (axs1[2], axs2[2]),
    ):
        ax.set_xlabel(xlabel)
        ax.axvline(0, color="grey", lw=0.5)
        ax.errorbar(
            df0[xcol] / xunit,
            df0["gate"],
            xerr=df0[f"{xcol}_err"] / xunit,
            color="k",
            marker="o",
        )

    # plot zero-field critical current
    df0 = df[df["field"] == 0]
    for ax in (axs1[1], axs2[1]):
        ax.set_xlabel(r"$I_\mathrm{c}$ (μA)")
        ax.axvline(0, color="grey", lw=0.5)
        for pm in "+-":
            ax.errorbar(
                df0[f"ic{pm} from fit"] / 1e-6,
                df0["gate"],
                xerr=df0[f"rmse{pm}"] / 1e-6,
                color="k",
                marker="o",
            )

    ## subtract zero-field offsets within in each trace
    # gb_cols = ["gate", "parent_csv"]
    # gb = df.groupby(gb_cols)
    # df = gb.apply(subtract_zerofield_offsets, include_groups=False)
    # df = df.reset_index(level=list(range(len(gb_cols))))
    # subtract field-mean
    df["delta"] -= df["delta_mean"]
    df["eta"] -= df["eta_mean"]

    # plot colormap of ΔIc(Β∥, Vg) and η(Β∥, Vg)
    df.sort_values(by=["field", "gate"], inplace=True)
    shape = df["field"].unique().size, df["gate"].unique().size
    for zcol, zlabel, zunit, ax in zip(
        ("eta", "delta"),
        (
            r"$\eta - \overline{\eta}$ (%)",
            r"$\Delta I_\mathrm{c} - \overline{\Delta I_\mathrm{c}}$ (nA)",
        ),
        (1 / 100, 1e-9),
        (axs1[0], axs2[0]),
    ):
        ax.set_xlabel(r"$B_\parallel$ (mT)")
        mesh = ax.pcolormesh(
            df["field"].values.reshape(shape) / 1e-3,
            df["gate"].values.reshape(shape),
            df[zcol].values.reshape(shape) / zunit,
            cmap="custom",
            norm=CenteredNorm(),
            rasterized=True,
        )
        cb = ax.get_figure().colorbar(
            mesh, ax=ax, location="top", orientation="horizontal"
        )
        cb.set_label(zlabel, labelpad=10)
    fig1.savefig(outsubdir / "eta.svg")
    fig2.savefig(outsubdir / "delta.svg")

outsubdir = outdir / "combined"
outsubdir.mkdir(exist_ok=True)

label_from_dirname = {
    "JS633-W2_Wsc=0.9um-ENE_WFS06_slopes": r"Device B, cooldown 6, $V_\text{g,init} = 0\,$V",
    "JS633-W2_Wsc=0.9um-ENE_WFS06_slopes+10Vreset": r"Device B, cooldown 6, $V_\text{g,init} = 10\,$V",
    "JS633-W2_Wsc=0.9um-NNE_WFS06_slopes": r"Device A, cooldown 6, $V_\text{g,init} = 10\,$V",
    "JS633-W2_Wsc=0.9um-NNE_WFS07_slopes": r"Device A, cooldown 7, $V_\text{g,init} = 10\,$V",
}

# plot zero-field slopes
slope_dfs = [read_csv(path) for path in slopepaths]
ic_dfs = [read_csv(path) for path in datapaths]
for df in slope_dfs + ic_dfs:
    df.sort_values(by="gate", inplace=True)
    df.drop(df[df["gate"] < -6.5].index, inplace=True)
for ycol, ylabel, yunit in zip(
    ("eta", "delta"),
    (
        (
            r"$\left.\frac{\partial\eta}{\partial B_\parallel}\right|_{B_\parallel=0}$"
            r" (%/mT)"
        ),
        (
            r"$\left.\frac{\partial(\Delta I_\mathrm{c})}{\partial"
            r" B_\parallel}\right|_{B_\parallel=0}$ (nA/mT)"
        ),
    ),
    ((1 / 100) / 1e-3, 1e-9 / 1e-3),
):
    fig, axs = plt.subplots(nrows=2, sharex=True)
    fig.set_figheight(1.5 * fig.get_figheight())
    axs[-1].set_xlabel(GATELABEL)
    axs[0].set_ylabel(ylabel)
    axs[1].set_ylabel(r"$I_\mathrm{c}$ (μA)")
    for ax in axs:
        ax.axhline(0, color="grey", lw=0.5)
    for df, path, icdf in zip(slope_dfs, slopepaths, ic_dfs):
        ebpts = axs[0].errorbar(
            df["gate"],
            df[f"{ycol}_slope"] / yunit,
            yerr=df[f"{ycol}_slope_err"] / yunit,
            lw=0.5,
            marker=".",
            ms=2,
            label=label_from_dirname[path.parent.name],
        )
        icdf = icdf[icdf["field"] == 0]
        for pm in "+-":
            axs[1].errorbar(
                icdf["gate"],
                icdf[f"ic{pm} from fit"] / 1e-6,
                yerr=icdf[f"rmse{pm}"] / 1e-6,
                color=ebpts.lines[0].get_color(),
                lw=0.5,
                marker=".",
                ms=2,
                label=label_from_dirname[path.parent.name] if pm == "+" else None,
            )
    axs[0].legend(fontsize="xx-small")
    axs[1].legend(fontsize="xx-small")
    fig.savefig(outsubdir / f"{ycol}.svg")
