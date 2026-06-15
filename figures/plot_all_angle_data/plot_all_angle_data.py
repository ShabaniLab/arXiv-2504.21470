# TODO plot fits in gate linecuts
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import colormaps
from matplotlib import pyplot as plt
from matplotlib import rcParams
from matplotlib.colors import CenteredNorm, LinearSegmentedColormap

THETALABEL = r"$\theta$"
GATELABEL = r"$V_\mathrm{g}$ (V)"
GATE_CUTS = [0, -2.6, -3.6, -5.25, -5.8]
XTICKS = [-180, -90, 0, 90, 180]
XTICKLABELS = [r"$-\pi$", r"$-\frac{\pi}{2}$", "0", r"$\frac{\pi}{2}$", r"$\pi$"]

plt.style.use(["paper", "onethirdpage"])
rcParams["font.size"] = 8

outdir = Path(Path(__file__).stem)
outdir.mkdir(exist_ok=True, parents=True)
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
for col in "delta", "eta":
    df[f"{col}_mean"] = df.groupby("gate")[f"{col}"].transform(lambda s: s.mean())
    df[f"{col}"] -= df[f"{col}_mean"]
# measure angle from current (+90°) and plot on domain [-π, π]
df["angle-from-I"] = ((((90 + df["angle-from-z"]) % 360) + 180) % 360) - 180
# merge duplicate angles (original endpoints θz=0,360° → θI=90°)
grouped = df.groupby(["gate", "angle-from-I"])
dfplt = grouped[["eta", "delta"]].agg("mean")
dfplt[["eta_err", "delta_err"]] = grouped[["eta_err", "delta_err"]].agg(
    lambda s: np.sqrt((s**2).sum()) / s.count()
)
dfplt = dfplt.reset_index()
# duplicate new endpoints (θI=-180° ≡ θI=+180°)
endpoints = dfplt[dfplt["angle-from-I"] == -180].copy()
endpoints["angle-from-I"] = 180
dfplt = pd.concat([dfplt, endpoints])
# unpack data
dfplt.sort_values(["angle-from-I", "gate"], inplace=True)
shape = dfplt["angle-from-I"].unique().size, dfplt["gate"].unique().size
θ = dfplt["angle-from-I"].values.reshape(shape)
Vg = dfplt["gate"].values.reshape(shape)

for zcol, zunit, zlabel, linecut_ylim, clim_halfrange in zip(
    ("eta", "delta"),
    (0.01, 1e-9),
    (
        r"$\eta - \overline{\eta}$ (%)",
        r"$\Delta I_\mathrm{c} - \overline{\Delta I_\mathrm{c}}$ (nA)",
    ),
    (1, 75),
    (1, 70),
):
    fig, ax = plt.subplots(figsize=(2, 2.1))
    ax.set_xlabel(THETALABEL)
    ax.set_ylabel(GATELABEL)
    ax.set_xticks(XTICKS)
    ax.set_xticklabels(XTICKLABELS)
    ax.text(
        0, 1, r"$B_\parallel=$20$\,$mT", transform=ax.transAxes, ha="left", va="bottom"
    )
    mesh = ax.pcolormesh(
        θ,
        Vg,
        dfplt[f"{zcol}"].values.reshape(shape) / zunit,
        rasterized=True,
        cmap="custom",
        norm=CenteredNorm(halfrange=clim_halfrange),
    )
    fig.colorbar(mesh, label=zlabel)
    # mark linecuts
    for gate in GATE_CUTS:
        ax.plot(
            np.array(
                [dfplt["angle-from-I"].min() - 7.5, df["angle-from-I"].min() + 15]
            ),
            [gate] * 2,
            "tab:pink",
            linewidth=1,
        )
    fig.savefig(outdir / f"pcolormesh_{zcol}.{rcParams['savefig.format']}")

    # plot linecuts at constant Vg
    fig, axs = plt.subplots(nrows=5, sharex=True, figsize=(1.2, 3))
    axs[-1].set_xlabel(THETALABEL)
    axs[2].set_ylabel(zlabel)
    axs[-1].set_xticks(XTICKS)
    axs[-1].set_xticklabels(XTICKLABELS)
    for ax, gate, text_xcoord, text_ha in zip(
        axs,
        GATE_CUTS,
        (0.03, 0.03, 0.03, 0.03, 0.03),
        ("left", "left", "left", "left", "left"),
    ):
        mask = dfplt["gate"] == gate
        ax.errorbar(
            dfplt[mask]["angle-from-I"],
            dfplt[mask][f"{zcol}"] / zunit,
            yerr=dfplt[mask][f"{zcol}_err"] / zunit,
            color="tab:pink",
            marker=">",
            ms=1,
            lw=0.5,
        )
        # linecut_ylim = max(np.abs(ax.get_ylim()))  # dynamic ylim
        ax.set_ylim((-linecut_ylim, linecut_ylim))  # symmetric ylim
        ax.text(
            text_xcoord,
            0.97,
            r"$V_\mathrm{g}=" f"{gate}\,$V",
            transform=ax.transAxes,
            ha=text_ha,
            va="top",
            fontsize="xx-small",
        )
        ax.axhline(0, color="lightgrey", lw=0.5)
        ax.axvline(0, color="lightgrey", lw=0.5)
    fig.savefig(outdir / f"linecuts_{zcol}.{rcParams['savefig.format']}")

# plot fit parameters vs. gate
df_fits = pd.read_csv("../../data/processed/centermax/JS633-W2/anglefits.csv")
df_fits.sort_values("gate", inplace=True)
# normalize fit parameters such that a1,3 > 0
for n in ("1", "3"):
    df_fits.loc[df_fits[f"a{n}"] < 0, f"φ{n}"] += 180
    df_fits.loc[df_fits[f"a{n}"] < 0, f"a{n}"] *= -1

# plot offset a0
fig, ax = plt.subplots()
ax.set_xlabel(GATELABEL)
ax.set_ylabel(r"$a_0$ (%)")
ax.axhline(0, color="lightgrey", lw=0.5)
ax.errorbar(
    df_fits["gate"], df_fits["a0"] / 0.01, yerr=df_fits["a0_err"] / 0.01, marker="o"
)
fig.savefig(outdir / f"fitparams_a0.{rcParams['savefig.format']}")
# plot amplitudes a1, a3 and phases φ1, φ3
fig, axs = plt.subplots(nrows=2, sharex=True, figsize=(7 / 3, 7 / 3 * 1.2))
axs[-1].set_xlabel(GATELABEL)
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
        label=f"$a_{n}$",
    )
    # plot phases φ1, φ3
    axs[1].errorbar(
        df_fits["gate"],
        df_fits[f"φ{n}"],
        yerr=df_fits[f"φ{n}_err"],
        marker=marker,
        label=f"$\\varphi_{n}$",
    )
zeropi_gates = (-2.7, -5.125)
for ax in axs:
    ax.axhline(0, color="lightgrey", lw=0.5)
    ax.axvspan(*zeropi_gates, color="tab:green", alpha=0.25)
    ax.legend()
axs[1].axhline(180, color="lightgrey", lw=0.5)
fig.savefig(outdir / f"fitparams.{rcParams['savefig.format']}")
