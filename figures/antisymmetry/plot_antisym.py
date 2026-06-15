from matplotlib import pyplot as plt
from pandas import read_csv

csv = read_csv(
    "../../data/processed/centermax/JS633-W2/Wsc=1.2um-E_diode-3.5V/data.csv"
)
mask = csv.iloc[:, 0].abs() <= 0.3
bfield = csv.iloc[:, 0][mask].values
icp = csv["ic+ from fit"][mask].values
icm = csv["ic- from fit"][mask].values
icp_err = csv["rmse+"][mask].values
icm_err = csv["rmse-"][mask].values

plt.style.use(["paper", "fullcolumn"])
fig, ax = plt.subplots()
# fig.set_figheight(1.175 * fig.get_figheight())
ax.set_xlabel("$B_\parallel$ (T)")
ax.set_ylabel(r"$I_\text{c}$ (μA)")
ax.axvline(0, c="grey", lw=0.5, zorder=-1)
# label gate and field angle
ax.text(
    0.02,
    0.98,
    r"$\theta=\pi/2$" "\n" r"$V_\text{g}=-3.5\,$V",
    transform=ax.transAxes,
    ha="left",
    va="top",
    fontsize="x-small",
)
# plot data
ax.errorbar(
    bfield,
    icp / 1e-6,
    yerr=icp_err / 1e-6,
    lw=0,
    marker="o",
    ms=2,
    label=r"$I_{\text{c}+}(B)$",
)
ax.errorbar(
    -bfield,
    -icm / 1e-6,
    yerr=icm_err / 1e-6,
    lw=0,
    marker="s",
    ms=2,
    mfc="none",
    label=r"$-I_{\text{c}-}(-B)$",
)
ax.set_ylim((0, None))
ax.legend()
fig.savefig("antisym.svg")
fig.savefig("antisym.pdf")
