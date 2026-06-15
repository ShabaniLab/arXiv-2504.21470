import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt
from pandas import read_csv
from scipy.interpolate import CubicSpline
from scipy.optimize import curve_fit

plt.style.use(["paper", "onethirdpage"])
fig, axs = plt.subplots(nrows=2, sharex=True)
fig.set_figheight(2 * fig.get_figheight())
axs[-1].set_xlabel(r"$\theta$")
axs[-1].set_xticks([-180, -90, 0, 90, 180])
axs[-1].set_xticklabels([r"$-\pi$", r"$-\pi/2$", "0", r"$\pi/2$", r"$\pi$"])

ax = axs[0]
ax.set_ylabel("$I_\mathrm{c}$ (μA)")
ax.axvline(0, c="lightgrey", lw=0.5, zorder=-1)
csv = read_csv(
    "../../../data/processed/centermax/JS633-W2/Wsc=0.6um-NNW_diode-angle-125mT/data.csv"
)
angle, icp, icm, icp_err, icm_err = csv.loc[
    :, ["in-plane angle-from-z", "ic+ from fit", "ic- from fit", "rmse+", "rmse-"]
].values.T
kwargsp = dict(color="tab:blue", zorder=5)
kwargsm = dict(color="tab:orange", zorder=10)


def angle_from_I(angle_from_z):
    """Measure angle from current direction (θ) instead of z-coil axis (θz).

    N.b. Wsc=0.6um-NNW was hooked up with I polarity such that angle_from_I = *-90* +
    angle_from_z.  However we inverted the current in invert_current.py to conform to
    the convention that (IxB).growth > 0.  Therefore the *+90* below is correct.
    """
    return (angle_from_z + 90) % 360


def sym_domain(theta, y):
    """Roll data onto the symmetric interval [-π, π], given theta ∈ [0, 2π]."""
    shift = -np.argmax(theta + 180 >= 360)
    new_theta = ((theta + 180) % 360) - 180
    new_theta = np.roll(new_theta, shift)
    new_theta = np.append(new_theta, np.abs(new_theta[0]))  # duplicate -180° at +180°
    new_y = np.roll(y, shift)
    new_y = np.append(new_y, new_y[0])
    return new_theta, new_y


ax.plot(
    *sym_domain(angle_from_I(angle), icp / 1e-6),
    label=r"$I_{\mathrm{c}+}$",
    lw=0,
    marker="o",
    **kwargsp,
)
ax.plot(
    *sym_domain(angle_from_I(angle), np.abs(icm) / 1e-6),
    label=r"$|I_{\mathrm{c}-}|$",
    lw=0,
    marker="s",
    **kwargsm,
)
# n.b. data endpoints θz=0 and 360 are both mapped to θ=90 by θ = (θz + 90) % 360;
# interpolate over the original θz domain [0, 360] to avoid duplicate points
angle_interp = np.arange(angle.min(), angle.max(), 1)
csp = CubicSpline(angle, icp)(angle_interp)
csm = CubicSpline(angle, np.abs(icm))(angle_interp)
angle_interp_sym, csp = sym_domain(angle_from_I(angle_interp), csp)
angle_interp_sym, csm = sym_domain(angle_from_I(angle_interp), csm)
split = np.argmax(angle_interp_sym == 90)
for s in (slice(None, split + 1), slice(split, None)):
    ax.plot(angle_interp_sym[s], csp[s] / 1e-6, **kwargsp)
    ax.plot(angle_interp_sym[s], csm[s] / 1e-6, **kwargsm)
ax.text(
    0,
    1.01,
    r"$B_\parallel=$125$\,$mT",
    transform=ax.transAxes,
    ha="left",
    va="bottom",
    fontsize="small",
)
ax.text(
    1,
    1.01,
    r"experiment",
    transform=ax.transAxes,
    ha="right",
    va="bottom",
    fontsize="small",
)
ax.legend(handletextpad=0.4, handlelength=1, fontsize="xx-small", loc="upper center")

###################
# diode vs. angle #
###################

ax = axs[-1]
ax.set_xlabel(r"$\theta$")
ax.set_ylabel("$\eta$ (%)")
ax.axhline(0, c="lightgrey", lw=0.5, zorder=-1)
ax.axvline(0, c="lightgrey", lw=0.5, zorder=-1)
eta = csv["eta"]
eta_err = csv["eta_err"]
# largest error bars are ~ ±0.2%
ax.plot(
    *sym_domain(angle_from_I(angle), eta * 100),
    label="experiment",
    lw=0,
    marker="o",
    color="k",
)


def sin(degrees, amplitude, θ0, a0):
    return a0 + amplitude * np.sin(np.radians(degrees + θ0))


popt, pcov = curve_fit(sin, angle + 90, eta)
# from fit: amplitude=0.04945108, offset=-1.587580deg
print(f"amplitude={popt[0]}, offset={popt[1]}deg")
x = np.arange(360)  # angle from I
ax.plot(
    *sym_domain(x, sin(x, *popt) * 100),
    "tab:gray",
    label=r"fit",
    zorder=-1,
)

mpl.rc("font", size=8)
ins = ax.inset_axes((0.53, 0.05, 0.45, 0.35))
ins.set_xlim(ax.get_xlim())
ins.set_xticks([-180, -90, 0, 90, 180])
ins.set_xticklabels([])
ins.set_yticks([0])
ins.set_yticklabels([])
ins.axhline(0, color="lightgrey", lw=0.25)
ins.axvline(0, color="lightgrey", lw=0.25)
angle_res = angle_from_I(angle)
angle_res_sym, residual = sym_domain(angle_res, eta - sin(angle_res, *popt))
angle_res_sym, res_err = sym_domain(angle_res, eta_err)
split = np.argmax(angle_res_sym == 90)
for s in (slice(None, split + 1), slice(split, None)):
    ins.errorbar(
        angle_res_sym,
        residual * 100,
        yerr=res_err * 100,
        lw=0.3,
        marker="o",
        ms=1.5,
        color="k",
    )
ax.legend(fontsize="small")
fig.savefig("experiment_angle.svg")
