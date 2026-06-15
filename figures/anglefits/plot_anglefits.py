import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

data = pd.read_csv("../../data/processed/centermax/JS633-W2/data_angle.csv")
# measure angle from current (+90°) and plot on domain [-π, π]
data["angle-from-I"] = ((((90 + data["angle-from-z"]) % 360) + 180) % 360) - 180
# duplicate new endpoints (θI=-180° ≡ θI=+180°)
endpoints = data[data["angle-from-I"] == -180].copy()
endpoints["angle-from-I"] = 180
data = pd.concat([data, endpoints])
data.sort_values(["gate", "angle-from-I"], inplace=True)

fits = pd.read_csv("../../data/processed/centermax/JS633-W2/anglefits.csv")
fits.sort_values("gate", inplace=True)

plt.style.use("paper")
fig, axs = plt.subplots(nrows=5, ncols=3, sharex=True, figsize=(7, 7))
for ax in axs[-1, :]:
    ax.set_xlabel(r"$\theta$")
    ax.set_xticks([-180, -90, 0, 90, 180])
    ax.set_xticklabels(["$-\pi$", "$-\pi/2$", "0", "$\pi/2$", "$\pi$"])
for ax in axs[:, 0]:
    ax.set_ylabel(r"$\eta$ (%)")
axs = np.array(axs).flatten(order="F")
for ax in axs:
    ax.axhline(0, color="lightgrey", lw=0.5)
    ax.axvline(0, color="lightgrey", lw=0.5)


θ = np.linspace(-180, 180)
alt_text_pos = [-5, -4.8, -4.2, -3.6, -3]
for i, (gate, group) in enumerate(data.groupby("gate")):
    ax = axs[i]
    ax.text(
        0.02,
        0.97 if gate not in alt_text_pos else 0.03,
        r"$V_\text{g}=" f"{gate:.3g}\,$V",
        transform=ax.transAxes,
        ha="left",
        va="top" if gate not in alt_text_pos else "bottom",
        fontsize="small",
    )
    fit = fits[fits["gate"] == gate]
    a0, a1, a3, φ1, φ3 = fit[["a0", "a1", "a3", "φ1", "φ3"]].values.squeeze()
    # plot raw data
    group["eta"] -= a0
    ebpts = ax.errorbar(
        group["angle-from-I"],
        group["eta"] / 0.01,
        yerr=group["eta_err"] / 0.01,
        lw=0,
        elinewidth=0.5,
        marker="o",
    )
    # plot dupilcated endpoint as an open circle
    mask = group["angle-from-I"] == 180
    ax.errorbar(
        group["angle-from-I"][mask],
        group["eta"][mask] / 0.01,
        yerr=group["eta_err"][mask] / 0.01,
        lw=0,
        marker="o",
        mfc="white",
        mec=ebpts.lines[0].get_color(),
    )
    # plot fit
    ax.plot(
        θ,
        (a1 * np.sin(np.radians(θ + φ1)) + a3 * np.sin(np.radians(3 * θ + φ3))) / 0.01,
        color="tab:orange",
    )

fig.savefig("matplotlib.svg")
