"""Plot JS633-W2 WAL data."""

import numpy as np
from matplotlib import pyplot as plt
from scipy.constants import e, h
from shabanipy.labber import ShaBlabberFile
from shabanipy.utils.plotting import cooldarkwarm

path = "2023/08/Data_0823/JS633-W2_Wsc@v3.1_LHB_WFS02-013.hdf5"
CH_XX = "source/Rxx - Value"
CH_YY = "ref/Ryy - Value"
CH_XY = "Rxy - Value"
CH_FIELD = "VectorMagnet - Field X"
CH_GATE = "gate 47 - Source voltage"
IBIAS_AC = 1e-6
BMAX = 0.03
BOFFSET = 1.75e-3
EXCLUDE_GATES = [-4.1, -4.2, -4.3, -4.4, -4.5]

filters = []
for g in EXCLUDE_GATES:
    filters.append((CH_GATE, lambda ch, g: ~np.isclose(ch, g), g))

with ShaBlabberFile(path) as f:
    gate, bfield, dvdixx, dvdiyy = f.get_data(
        CH_GATE,
        CH_FIELD,
        CH_XX,
        CH_YY,
        order=(CH_GATE, CH_FIELD),
        filters=filters,
    )
rxx = (dvdixx / IBIAS_AC).real
ryy = (dvdiyy / IBIAS_AC).real
bfield -= BOFFSET

#plt.style.use(["thesis", "halfpage"])
cmap = plt.get_cmap("coolwarm")

fig, ax = plt.subplots(figsize=(4, 4))
fig.set_figheight(fig.get_figwidth())
ax.axvline(0, color="lightgrey", lw=0.5)
ax.set_xlabel(r"$B_\perp$ (mT)")
ax.set_ylabel(r"$\Delta\sigma_{(xx+yy)/2}$ ($e^2/h$)")
for i, (g, b, r) in enumerate(zip(reversed(gate), bfield, reversed((rxx + ryy) / 2))):
    mask = (-BMAX < b) & (b < BMAX)
    g, b, r = g[mask], b[mask], r[mask]
    s = 1 / r
    s -= s.mean()
    ax.plot(b / 1e-3, s / (e**2 / h), "-", lw=0.5, color=cmap(i / (rxx.shape[0] - 1)))
ax.text(
    30,
    0.2,
    f"$V_\mathrm{{g}}={gate.min():.1f}\,$V",
    color=cmap(0.999),
    ha="right",
    va="bottom",
)
ax.text(
    30,
    -0.1,
    f"$V_\mathrm{{g}}={gate.max():.1f}\,$V",
    color=cmap(0),
    ha="right",
    va="top",
)
fig.savefig("wal1.pdf")

cooldarkwarm.register()
cmap = plt.get_cmap("cooldarkwarm_r")
fig, axs = plt.subplots(ncols=2, sharey=True, sharex=True, figsize=(8.5 - 2, 11 - 3))
for ax in axs:
    ax.set_xlabel(r"$B_\perp$ (mT)")
axs[0].set_ylabel(r"$\Delta\sigma_{xx}^\mathrm{sym}$ ($e^2/h$)")
axs[1].set_ylabel(r"$\Delta\sigma_{yy}^\mathrm{sym}$ ($e^2/h$)")
for ax, res in zip(axs, (rxx, ryy)):
    for i, (g, b, r) in enumerate(zip(gate, bfield, res)):
        mask = (-BMAX < b) & (b < BMAX)
        g, b, r = g[mask], b[mask], r[mask]
        s = 1 / r
        s = (s[::] + s[::-1]) / 2
        s -= s.mean()
        s += i * 5e-6
        ax.plot(
            b / 1e-3, s / (e**2 / h), "-", lw=1, color=cmap(i / (rxx.shape[0] - 1))
        )
    ax.text(
        -30,
        -0.025,
        f"$V_\mathrm{{g}}={gate.min():.1f}\,$V",
        color=cmap(0),
        ha="left",
        va="top",
    )
    ax.text(
        -30,
        7.4,
        f"$V_\mathrm{{g}}={gate.max():.1f}\,$V",
        color=cmap(0.99999),
        ha="left",
        va="bottom",
    )
axs[0].set_ylim((-0.2, 8.05))
fig.savefig("wal2_unlabeled.pdf")
