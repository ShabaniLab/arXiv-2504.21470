from collections import defaultdict
from pathlib import Path

import numpy as np
from matplotlib import colormaps
from matplotlib import pyplot as plt
from matplotlib import rcParams
from matplotlib.colors import CenteredNorm, LinearSegmentedColormap
from pandas import read_csv

BLABEL = r"$B_\parallel$ (mT)"
ETALABEL = r"$\eta - \overline{\eta}$ (%)"
GATELABEL = r"$V_\mathrm{g}$ (V)"
GATEMIN, GATEMAX = -6.5, 0

plt.style.use(["paper", "onethirdpage"])
rcParams["font.size"] = 8

# custom colormap
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


datasets = [
    dict(
        path=Path(
            # "../../data/processed/centermax/JS633-W2_Wsc=0.9um-ENE_WFS06_slopes"
            "../../data/processed/centermax/JS633-W2_Wsc=0.9um-ENE_WFS06_slopes+10Vreset"
        ),
        device="0.9-ENE",
        gate_cuts=(-6, -5.5, -4.5, -3.6, -3),
        color="tab:green",
        marker="s",
        label=r"$I \parallel [1\overline{1}0]$",
        ylim=1.5,
    ),
    dict(
        path=Path("../../data/processed/centermax/JS633-W2_Wsc=0.9um-NNE_WFS06_slopes"),
        device="0.9-NNE",
        gate_cuts=(-6.25, -5.25, -3.75, -2.25, -1),
        color="tab:pink",
        marker="o",
        label=r"$I \parallel [110]$",
        ylim=1.4,
    ),
]
i = 1  # select dataset for colormap and linecuts
gate_cuts = datasets[i]["gate_cuts"]
df = read_csv(datasets[i]["path"] / "data_deduped.csv")
df = df[(GATEMIN <= df["gate"]) & (df["gate"] <= GATEMAX)]
# subtract gate-dependent mean
df["eta_mean"] = df.groupby("gate")["eta"].transform(lambda s: s.mean())
df["eta"] -= df["eta_mean"]
# df = (
#    df.groupby("gate")
#    .apply(subtract_zerofield_offsets, include_groups=False)
#    .reset_index(level=0)
# )
df.sort_values(by=["field", "gate"], inplace=True)
shape = df["field"].unique().size, df["gate"].unique().size

# plot Ic(Vg) and η(Vg, B∥) colormap
fig, axs = plt.subplots(ncols=2, sharey=True, width_ratios=[1, 2])
fig.set_figwidth(1.1 * fig.get_figwidth())
fig.set_figheight(1.25 * fig.get_figheight())
axs[0].set_ylabel(GATELABEL)
axs[0].set_xlabel(r"$I_\mathrm{c}$ (μA)")
axs[1].set_xlabel(BLABEL)
mask = df["field"] == 0
axs[0].plot(
    df[[f"ic{pm} from fit" for pm in "+-"]].abs().mean(axis=1)[mask] / 1e-6,
    df["gate"][mask],
    ".k-",
)
mesh = axs[1].pcolormesh(
    df["field"].values.reshape(shape) / 1e-3,
    df["gate"].values.reshape(shape),
    df["eta"].values.reshape(shape) / (1 / 100),
    cmap="custom",
    norm=CenteredNorm(),
    rasterized=True,
)
fig.colorbar(mesh, ax=axs[1], label=ETALABEL)
# mark linecuts
for gate in gate_cuts:
    axs[1].plot(
        np.array([df["field"].min() - 0.0025, df["field"].min() + 0.0050]) / 1e-3,
        [gate] * 2,
        datasets[i]["color"],
        linewidth=1,
    )
axs[0].text(
    0,
    1,
    r"$B_\parallel = 0$",
    transform=axs[0].transAxes,
    ha="left",
    va="bottom",
    fontsize="small",
)
axs[1].text(
    0.98,
    0.98,
    datasets[i]["label"],
    transform=axs[1].transAxes,
    ha="right",
    va="top",
    fontsize="small",
    bbox=dict(facecolor="w", alpha=0.5, lw=0.5, boxstyle="round,pad=0.1"),
)
axs[1].text(
    0,
    1,
    r"$\theta=\pi/2$",
    transform=axs[1].transAxes,
    ha="left",
    va="bottom",
    fontsize="small",
)
axs[0].set_xlim((0, None))
fig.savefig(f"ic+pcolormesh.{rcParams['savefig.format']}")

# plot linecuts: η(B∥) at constant Vg
fig, axs = plt.subplots(nrows=5, sharex=True)
fig.set_figheight(1.8 * fig.get_figheight())
fig.set_figwidth(0.45 * fig.get_figwidth())
axs[-1].set_xlabel(BLABEL, fontsize="small")
axs[2].set_ylabel(ETALABEL)
for ax in axs:
    ax.axhline(0, color="lightgrey", lw=0.5)
    ax.axvline(0, color="lightgrey", lw=0.5)
for ax, gate in zip(reversed(axs), gate_cuts):
    mask = df["gate"] == gate
    ax.errorbar(
        df[mask]["field"] / 1e-3,
        df[mask]["eta"] / (1 / 100),
        yerr=df[mask]["eta_err"] / (1 / 100),
        color=datasets[i]["color"],
        marker=datasets[i]["marker"],
        ms=1,
        lw=0.5,
    )
    # ylim = max(np.abs(ax.get_ylim()))  # dynamic ylim
    ylim = datasets[i]["ylim"]  # uniform ylim
    ax.set_ylim((-ylim, ylim))  # symmetric ylim
    ax.text(
        0.03,
        0.97,
        r"$V_\mathrm{g}=" f"{gate}\,$V",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize="xx-small",
    )
fig.savefig(f"linecuts.{rcParams['savefig.format']}")

# plot zero-field dη/dB and B*
MS = 1.5
fig, axs = plt.subplots(nrows=2, sharex=True)
fig.set_figwidth(0.8 * fig.get_figwidth())
fig.set_figheight(1.5 * fig.get_figheight())
axs[0].set_ylabel(
    r"$\left.\frac{\partial\eta}{\partial B_\parallel}\right|_{B_\parallel=0}$ (%/T)"
)
axs[1].set_ylabel(r"$B_*$ (mT)")
axs[1].set_xlabel(GATELABEL)
for ax in axs:
    ax.axhline(0, color="k", lw=0.5)
for ds in datasets:
    # plot dη/dΒ
    df = read_csv(ds["path"] / "slopes_deduped.csv")
    df.sort_values(by="gate", inplace=True)
    df = df[(GATEMIN <= df["gate"]) & (df["gate"] <= GATEMAX)]
    axs[0].errorbar(
        df["gate"],
        df["eta_slope"] / 0.01,
        yerr=df["eta_slope_err"] / 0.01,
        color=ds["color"],
        marker=ds["marker"],
        label=ds["label"],
        lw=0.5,
        ms=MS,
    )
    # plot B*
    df = read_csv(ds["path"] / "bstar_deduped.csv")
    df = df[(GATEMIN <= df["gate"]) & (df["gate"] <= GATEMAX)]
    df.sort_values(by="gate", inplace=True)
    ax.errorbar(
        df["gate"],
        df["bstar"] / 1e-3,
        yerr=df["bstar_err"] / 1e-3,
        color=ds["color"],
        marker=ds["marker"],
        label=ds["label"],
        lw=0.5,
        ms=MS,
    )

axs[0].legend(fontsize="xx-small", loc="upper center")
fig.savefig(f"slope+bstar.{rcParams['savefig.format']}")
