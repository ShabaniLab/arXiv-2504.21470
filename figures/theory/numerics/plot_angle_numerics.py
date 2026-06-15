import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit

with np.load("diode_effect_vs_angle_beta1.1.npz", allow_pickle=True) as f:
    Jcp = f["Jcp"]
    Jcm = f["Jcm"]

icp, icm = Jcp[2], Jcm[2]
eta = (icp - icm) / (icp + icm)
angle = np.linspace(-np.pi, np.pi, len(icp))
Lx, Ly = 2.5, 2.5  # units of ξ0
Lsq = Lx * Ly

plt.style.use(["paper", "onethirdpage"])
fig, axs = plt.subplots(nrows=2, sharex=True)
fig.set_figheight(2 * fig.get_figheight())
axs[-1].set_xlabel(r"$\theta$")
axs[-1].set_xticks([-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi])
axs[-1].set_xticklabels([r"$-\pi$", r"$-\pi/2$", "0", r"$\pi/2$", r"$\pi$"])

#################
# Jc± vs. angle #
#################

ax = axs[0]
ax.set_ylabel(r"$J_\mathrm{c}$ ($e/\xi_0^2$)")
ax.axvline(0, c="lightgrey", lw=0.5, zorder=-1)
ax.plot(
    angle, icp / Lsq, label=r"$J_{\mathrm{c}+}$", marker="o", color="tab:blue", zorder=5
)
ax.plot(
    angle,
    icm / Lsq,
    label=r"$|J_{\mathrm{c}-}|$",
    marker="s",
    color="tab:orange",
    zorder=10,
)
ax.text(
    1,
    1.01,
    r"theory",
    transform=ax.transAxes,
    ha="right",
    va="bottom",
    fontsize="small",
)
ax.set_yticks([0.232, 0.2325, 0.233, 0.2335, 0.234, 0.2345])
ax.set_yticklabels(["0.232", "", "0.233", "", "0.234", ""])
ax.legend(handletextpad=0.4, handlelength=1, fontsize="xx-small", loc="upper center")

###################
# diode vs. angle #
###################

ax = axs[-1]
ax.set_xlabel(r"$\theta$")
ax.set_ylabel("$\eta$ (%)")
ax.axhline(0, c="lightgrey", lw=0.5, zorder=-1)
ax.axvline(0, c="lightgrey", lw=0.5, zorder=-1)
ax.plot(
    angle,
    eta / 0.01,
    label="theory",
    lw=0,
    marker="o",
    color="k",
)
ax.legend()


def sin(radians, amplitude, offset):
    return amplitude * np.sin(radians + offset)


popt, pcov = curve_fit(sin, angle, eta)
x = np.linspace(-np.pi, np.pi)
ax.plot(
    x,
    sin(x, *popt) / 0.01,
    "tab:gray",
    label=r"fit",
    zorder=-1,
)
mpl.rc("font", size=8)
ins = ax.inset_axes((0.53, 0.05, 0.45, 0.35))
ins.set_xlim(ax.get_xlim())
ins.set_xticks([-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi])
ins.set_xticklabels([])
ins.set_yticks([0])
ins.set_yticklabels([])
ins.axhline(0, color="lightgrey", lw=0.25)
ins.axvline(0, color="lightgrey", lw=0.25)
ins.plot(
    angle,
    (eta - sin(angle, *popt)) / 0.01,
    lw=0.3,
    marker="o",
    ms=1.5,
    color="k",
)
ax.legend(fontsize="small")
fig.savefig("numerics_angle.svg")
