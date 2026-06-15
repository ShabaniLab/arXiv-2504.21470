from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt

indir = Path("../../data/processed/centermax/JS633-W2_Wsc=0.9um-NNE_WFS07_slopes")
tests = {
    "0field-offset-tests": dict(
        label="baseline",
        gate=-5.25,
    ),
    "0field-offset-tests_swap-dmm-polarity": dict(
        label="swap $V$ polarity",
        gate=-5.25,
    ),
    "0field-offset-tests_swap-yoko&dmm-polarity": dict(
        label="swap $V$ and $I$ polarities",
        gate=-5.25,
    ),
    "0field-offset-tests_no-amp": dict(
        label="remove $V$ amplifier",
        gate=-5.25,
    ),
    "0field-offset-tests_new-gate-keithley": dict(
        label="change gate voltage source",
        gate=-5.25,
    ),
    "0field-offset-tests_+500mT-polarization": dict(
        label="initialize to $B_\parallel=+500\,$mT",
        gate=-4.8,
    ),
    "0field-offset-tests_-500mT-polarization": dict(
        label="initialize to $B_\parallel=-500\,$mT",
        gate=-4.8,
    ),
}
group1 = [
    "0field-offset-tests",
    "0field-offset-tests_swap-dmm-polarity",
    "0field-offset-tests_swap-yoko&dmm-polarity",
    "0field-offset-tests_no-amp",
    # "0field-offset-tests_new-gate-keithley",
]
group2 = [
    "0field-offset-tests_+500mT-polarization",
    "0field-offset-tests_-500mT-polarization",
]

plt.style.use(["paper", "fullcolumn"])
fig, ax = plt.subplots()
ax.axhline(0, color="grey", lw=0.5)
ax.axvline(0, color="grey", lw=0.5)
ax.set_xlabel(r"$B_\parallel$ (mT)")
ax.set_ylabel(r"$\eta$ (%)")
for test in group1:
    params = tests[test]
    csv = pd.read_csv(indir / test / "data.csv")
    ax.errorbar(
        csv["in-plane magnitude"] / 1e-3,
        csv["eta"] / 0.01,
        yerr=csv["eta_err"] / 0.01,
        label=params["label"],
        marker="o",
    )
ax.text(
    0.5,
    1,
    r"$V_\text{g}=-5.25\,$V",
    transform=ax.transAxes,
    fontsize="small",
    ha="center",
    va="bottom",
)
ax.legend(fontsize="xx-small")
fig.savefig("zero-field-offset-tests1.svg")

fig, ax = plt.subplots()
ax.axhline(0, color="grey", lw=0.5)
ax.axvline(0, color="grey", lw=0.5)
ax.set_xlabel(r"$B_\parallel$ (mT)")
ax.set_ylabel(r"$\eta$ (%)")
for test in group2:
    params = tests[test]
    csv = pd.read_csv(indir / test / "data.csv")
    ax.errorbar(
        csv["in-plane magnitude"] / 1e-3,
        csv["eta"] / 0.01,
        yerr=csv["eta_err"] / 0.01,
        label=params["label"],
        marker="o",
    )
ax.text(
    0.5,
    1,
    r"$V_\text{g}=-4.8\,$V",
    transform=ax.transAxes,
    fontsize="small",
    ha="center",
    va="bottom",
)
ax.legend(fontsize="xx-small")
fig.savefig("zero-field-offset-tests2.svg")
