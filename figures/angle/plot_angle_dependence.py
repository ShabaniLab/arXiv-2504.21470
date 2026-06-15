"""Plot angle data for Wsc=0.9um-NNE (I ∥ [110])."""
from collections import defaultdict

import numpy as np
import pandas as pd
from matplotlib import colormaps
from matplotlib import pyplot as plt
from matplotlib import rcParams
from matplotlib.colors import CenteredNorm, LinearSegmentedColormap

THETALABEL = r"$\theta$"
ETALABEL = r"$\eta - \overline{\eta}$ (%)"
GATELABEL = r"$V_\mathrm{g}$ (V)"
THETA_TICKS = [-180, -90, 0, 90, 180]
THETA_TICKLABELS = [r"$-\pi$", r"$-\frac{\pi}{2}$", "0", r"$\frac{\pi}{2}$", r"$\pi$"]
GATE_CUTS = [0, -2.6, -3.6, -5.25, -5.8]

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

df = pd.read_csv("../../data/processed/centermax/JS633-W2/data_angle.csv")
# subtract gate-dependent mean
df["eta_mean"] = df.groupby("gate")["eta"].transform(lambda s: s.mean())
df["eta"] -= df["eta_mean"]
# measure angle from current (+90°) and plot on domain [-π, π]
df["angle-from-I"] = ((((90 + df["angle-from-z"]) % 360) + 180) % 360) - 180
# merge duplicate angles (original endpoints θz=0,360° → θI=90°)
grouped = df.groupby(["gate", "angle-from-I"])
df = grouped[["ic+ from fit", "ic- from fit", "eta"]].agg("mean")
df["eta_err"] = grouped["eta_err"].agg(lambda s: np.sqrt((s**2).sum()) / s.count())
df = df.reset_index()
# duplicate new endpoints (θI=-180° ≡ θI=+180°)
endpoints = df[df["angle-from-I"] == -180].copy()
endpoints["angle-from-I"] = 180
df = pd.concat([df, endpoints])
# unpack data
df.sort_values(["angle-from-I", "gate"], inplace=True)
shape = df["angle-from-I"].unique().size, df["gate"].unique().size

# plot Ic(Vg) and η(Vg, θ) colormap
fig, axs = plt.subplots(ncols=2, sharey=True, width_ratios=[1, 2])
fig.set_figwidth(1.1 * fig.get_figwidth())
fig.set_figheight(1.25 * fig.get_figheight())
axs[0].set_ylabel(GATELABEL)
axs[0].set_xlabel(r"$I_\mathrm{c}$ (μA)")
axs[1].set_xlabel(THETALABEL)
axs[1].set_xticks(THETA_TICKS)
axs[1].set_xticklabels(THETA_TICKLABELS)
mask = df["angle-from-I"] == 0
axs[0].plot(
    df[[f"ic{pm} from fit" for pm in "+-"]].abs().mean(axis=1)[mask] / 1e-6,
    df["gate"][mask],
    ".k-",
)
mesh = axs[1].pcolormesh(
    df["angle-from-I"].values.reshape(shape),
    df["gate"].values.reshape(shape),
    df["eta"].values.reshape(shape) / 0.01,
    rasterized=True,
    cmap="custom",
    norm=CenteredNorm(halfrange=1),
)
fig.colorbar(mesh, ax=axs[1], label=ETALABEL)
# mark linecuts
for gate in GATE_CUTS:
    axs[1].plot(
        np.array([df["angle-from-I"].min() - 7.5, df["angle-from-I"].min() + 15]),
        [gate] * 2,
        "tab:pink",
        linewidth=1,
    )
axs[0].text(
    0,
    1,
    r"$\theta = 0$",
    transform=axs[0].transAxes,
    ha="left",
    va="bottom",
    fontsize="small",
)
axs[1].text(
    0.98,
    0.98,
    r"$I \parallel [110]$",
    transform=axs[1].transAxes,
    ha="right",
    va="top",
    fontsize="small",
    bbox=dict(facecolor="w", alpha=0.5, lw=0.5, boxstyle="round,pad=0.1"),
)
axs[1].text(
    0,
    1,
    r"$B_\parallel=$20$\,$mT",
    transform=axs[1].transAxes,
    ha="left",
    va="bottom",
    fontsize="small",
)
axs[0].set_xlim((0, None))
fig.savefig(f"ic+pcolormesh.{rcParams['savefig.format']}")

# plot linecuts: η(θ) at constant Vg
fig, axs = plt.subplots(nrows=5, sharex=True, figsize=(1.2, 3))
axs[-1].set_xlabel(THETALABEL)
axs[2].set_ylabel(ETALABEL, labelpad=8)
axs[-1].set_xticks(THETA_TICKS)
axs[-1].set_xticklabels([r"$-\pi$", "", "0", "", r"$\pi$"])
for ax in axs:
    ax.axhline(0, color="lightgrey", lw=0.5)
    ax.axvline(0, color="lightgrey", lw=0.5)
for ax, gate, ylim, ytick in zip(
    axs, GATE_CUTS, [1, 0.27, 1, 0.27, 1], [1, 0.2, 1, 0.2, 1]
):
    mask = df["gate"] == gate
    ax.errorbar(
        df[mask]["angle-from-I"],
        df[mask]["eta"] / 0.01,
        yerr=df[mask]["eta_err"] / 0.01,
        color="tab:pink",
        marker="o",
        ms=1,
        lw=0.5,
    )
    # ylim = max(np.abs(ax.get_ylim()))  # dynamic ylim
    # ylim = 1  # uniform ylim
    ax.set_ylim((-ylim, ylim))  # symmetric ylim
    ax.set_yticks([-ytick, 0, ytick])
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

# plot fit parameters vs. gate
df_fits = pd.read_csv("../../data/processed/centermax/JS633-W2/anglefits.csv")
df_fits.sort_values("gate", inplace=True)
# normalize fit parameters such that a1,3 > 0
for n in ("1", "3"):
    df_fits.loc[df_fits[f"a{n}"] < 0, f"φ{n}"] += 180
    df_fits.loc[df_fits[f"a{n}"] < 0, f"a{n}"] *= -1

# plot amplitudes a1, a3 and phases φ1, φ3
MS = 2
fig, axs = plt.subplots(nrows=2, sharex=True)
fig.set_figwidth(0.8 * fig.get_figwidth())
fig.set_figheight(1.5 * fig.get_figheight())
axs[1].set_xlabel(GATELABEL)
axs[0].set_ylabel(r"$a_n$ (%)")
axs[1].set_ylabel(r"$\varphi_n$")
axs[1].set_yticks([0, 90, 180])
axs[1].set_yticklabels(["0", r"$\pi/2$", r"$\pi$"])
for n, marker in zip((1, 3), ("o", "s")):
    # plot amplitudes a1, a3
    axs[0].errorbar(
        df_fits["gate"],
        df_fits[f"a{n}"] / 0.01,
        yerr=df_fits[f"a{n}_err"] / 0.01,
        marker=marker,
        ms=MS,
        label=f"$a_{n}$",
    )
    # plot phases φ1, φ3
    axs[1].errorbar(
        df_fits["gate"],
        df_fits[f"φ{n}"],
        yerr=df_fits[f"φ{n}_err"],
        marker=marker,
        ms=MS,
        label=f"$\\varphi_{n}$",
    )
zeropi_gates = (-2.7, -5.125)
for ax in axs:
    ax.axhline(0, color="lightgrey", lw=0.5)
    ax.axvspan(*zeropi_gates, color="tab:green", alpha=0.25)
    ax.legend()
axs[1].axhline(180, color="lightgrey", lw=0.5)
axs[0].set_ylim((0, None))
fig.savefig(f"fitparams.{rcParams['savefig.format']}")
