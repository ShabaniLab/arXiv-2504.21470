from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from pandas import read_csv

csv = read_csv(
    "../../data/processed/centermax/JS633-W2/Wsc=1.2um-E_diode-3.5V/data.csv"
)
mask = csv.iloc[:, 0].abs() <= 0.3
bfield = csv.iloc[:, 0][mask].values
eta = csv["eta"][mask].values
eta_err = csv["eta_err"][mask].values

plt.style.use(["paper", "onethirdpage"])
fig, ax = plt.subplots()
fig.set_figheight(1.175 * fig.get_figheight())
ax.set_xlabel("$B_\parallel$ (T)")
ax.set_ylabel("$\eta$ (%)")
ax.axhline(0, c="grey", lw=0.5, zorder=-1)
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
ax.plot(
    bfield,
    eta / 0.01,
    lw=0.5,
    marker="o",
    ms=1,
    c="k",
)
# plot uncertainty (negligible at this scale)
ax.fill_between(
    bfield,
    (eta + eta_err) / 0.01,
    (eta - eta_err) / 0.01,
    alpha=0.5,
    facecolor="k",
)
# highlight slope inversion
rect = Rectangle((-55e-3, -1.5), 110e-3, 3, lw=0, fc="tab:olive", alpha=0.5)
ax.add_patch(rect)
fig.savefig("in-plane.svg")
