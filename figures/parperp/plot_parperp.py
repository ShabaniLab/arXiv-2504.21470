"""Plot Wsc=0.6um-NNW η(B∥) data for B∥ both ∥ and ⊥ to I."""
from matplotlib import pyplot as plt
from pandas import read_csv

plt.style.use(["paper", "fullcolumn"])

csvs = [
    read_csv("../../data/processed/centermax/JS633-W2/Wsc=0.6um-NNW_diode-y/data.csv"),
    read_csv(
        "../../data/processed/centermax/JS633-W2/Wsc=0.6um-NNW_diode-0V/data_qca.csv"
    ),
]
fig, ax = plt.subplots()
ax.set_xlabel("$B_\parallel$ (T)")
ax.set_ylabel("$\eta$ (%)")
ax.axhline(0, c="lightgrey", lw=0.5, zorder=-1)
ax.axvline(0, c="lightgrey", lw=0.5, zorder=-1)
csvs[0].loc[:, "VectorMagnet - Field Y"] *= -1  # 180° → 0° (sign convention)
for csv, kwargs in zip(
    csvs,
    (
        dict(
            lw=0.5,
            marker="o",
            ms=1,
            c="k",
            label=r"$\theta=0$",
        ),
        dict(lw=0.5, marker="s", ms=1, c="tab:blue", label=r"$\theta=\pi/2$"),
    ),
):
    bfield = csv.iloc[:, 0].values
    eta = csv["eta"].values
    eta_err = csv["eta_err"].values
    ax.plot(bfield, eta * 100, **kwargs)
    ax.fill_between(
        bfield,
        (eta + eta_err) * 100,
        (eta - eta_err) * 100,
        alpha=0.5,
        facecolor=kwargs["c"],
    )
ax.legend(handlelength=1.5)
fig.savefig("parperp.svg", bbox_inches="tight")
fig.savefig("parperp.pdf", bbox_inches="tight")
