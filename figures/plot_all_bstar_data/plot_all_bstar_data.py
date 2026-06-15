"""Plot all zero-field slope data.

Plot B*(Vg) from all fits.
"""
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rcParams
from numpy.polynomial import Polynomial
from pandas import read_csv

BLABEL = r"$B_\parallel$ (mT), $\theta=\pi/2$"
ETALABEL = r"$\eta - \eta_0$ (%)"
GATELABEL = r"$V_\mathrm{g}$ (V)"
FIGSIZE = (6, 3.375)
wsc_kwargs = {
    "0.3-N": dict(
        color="tab:purple",
        marker="x",
        ls="solid",
        label=r"$W_\mathrm{sc}=$0.3$\,$μm",
        zorder=8,
    ),
    "0.6-NNW": dict(
        color="tab:blue",
        marker="D",
        ls="solid",
        label=r"$W_\mathrm{sc}=$0.6$\,$μm",
        zorder=7,
    ),
    "0.9-ENE": dict(
        color="tab:green",
        marker="s",
        ls="solid",
        label=r"$W_\mathrm{sc}=$0.9$\,$μm (Device B)",
        zorder=6,
    ),
    "1.2-E": dict(
        color="tab:orange",
        marker="^",
        ls="solid",
        label=r"$W_\mathrm{sc}=$1.2$\,$μm",
        zorder=5,
    ),
    "inf-SSE": dict(
        color="tab:red",
        marker="o",
        ls="solid",
        label=r"$W_\mathrm{sc}\rightarrow\infty$",
        zorder=4,
    ),
}

plt.style.use(["paper", "fullcolumn"])
outdir = Path(__file__).parent

# plot B*(Vg) for each Wsc
fig, ax = plt.subplots(figsize=FIGSIZE)
ax.set_xlabel(GATELABEL)
ax.set_ylabel("$B_*$ (mT)")
ax.axhline(0, color="grey", lw=0.5, zorder=-10)
XTICKS = np.arange(-6, 11, 2)
ax.set_xticks(XTICKS)
fits = read_csv("../../data/processed/fitresults.csv")
fits = fits.sort_values(["wsc", "gate"], ascending=[False, True])
# use Wsc=inf Vg=-3V scan with less-pronounced 0-field dip anomaly
fits.drop(
    fits[fits["datapath"].str.contains("/Wsc=inf-SSE_diode-3V/")].index, inplace=True
)
for device, df in fits.groupby("device", sort=False):
    ax.errorbar(
        df["gate"],
        df["bstar"] / 1e-3,
        yerr=df["bstar_err"] / 1e-3,
        color=wsc_kwargs[device]["color"],
        label=wsc_kwargs[device]["label"],
        marker=wsc_kwargs[device]["marker"],
        zorder=wsc_kwargs[device]["zorder"],
    )

## eyeballed B*(α) from lotfizadeh2024 arxiv:2303.01902v1 Fig. 3b
alpha = [2, 4, 6, 8, 10, 12]  # meV.nm
bstar = np.array([0.44, 1.14, 1.84, 2.52, 3.19, 3.87]) / 4.06 * 20  # mT
fit = Polynomial.fit(alpha, bstar, 1)
alpha_ticks = np.array([0, 10, 20])
# ax2 = ax.twinx()
# ax2.tick_params(axis="y", which="both", right=True, labelright=False)
# ax2.set_ylabel(r"$\longleftarrow\tau\qquad\alpha\longrightarrow$")
# ax2.set_ylim(ax.get_ylim())
# ax2.set_yticks(fit(alpha_ticks))
# ax2.set_yticklabels([])
# ax2.set_yticklabels(alpha_ticks)
# ax2.set_ylabel(r"$\alpha$ (meV$\,$nm)")

kwargs = {
    "JS633-W2_Wsc=0.9um-ENE_WFS06_slopes": dict(
        color="yellowgreen",
        marker="s",
        ls="solid",
        label=r"$W_\mathrm{sc}=$0.9$\,$μm (Device B, cooldown 6, $V_\text{g,init} = 0\,$V)",
        zorder=-10,
    ),
    "JS633-W2_Wsc=0.9um-ENE_WFS06_slopes+10Vreset": dict(
        color="lightgreen",
        marker="s",
        ls="solid",
        label=r"$W_\mathrm{sc}=$0.9$\,$μm (Device B, cooldown 6, $V_\text{g,init} = 10\,$V)",
        zorder=-10,
    ),
    "JS633-W2_Wsc=0.9um-NNE_WFS06_slopes": dict(
        color="tab:pink",
        marker=">",
        ls="solid",
        label=r"$W_\mathrm{sc}=$0.9$\,$μm (Device A, cooldown 6, $V_\text{g,init} = 10\,$V)",
        zorder=-10,
    ),
    "JS633-W2_Wsc=0.9um-NNE_WFS07_slopes": dict(
        color="lightpink",
        marker=">",
        ls="solid",
        label=r"$W_\mathrm{sc}=$0.9$\,$μm (Device A, cooldown 7, $V_\text{g,init} = 10\,$V)",
        zorder=-10,
    ),
}

# plot B*(Vg) from 4 slope-inversion datasets
for dir_ in kwargs.keys():
    df = read_csv(Path(f"../../data/processed/centermax/{dir_}/bstar_deduped.csv"))
    df.drop(df[df["gate"] < -6.5].index, inplace=True)
    df.sort_values(by="gate", inplace=True)
    ax.errorbar(
        df["gate"],
        df["bstar"] / 1e-3,
        yerr=df["bstar_err"] / 1e-3,
        color=kwargs[dir_]["color"],
        label=kwargs[dir_]["label"],
        marker=kwargs[dir_]["marker"],
        zorder=kwargs[dir_]["zorder"],
    )

ax.legend(fontsize="xx-small", bbox_to_anchor=(1, 1), loc="upper left")
fig.savefig(outdir / f"matplotlib.{rcParams['savefig.format']}")
