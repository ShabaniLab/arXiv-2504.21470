"""Fit slope of ΔIc(B∥) and η(B∥) at B∥=0."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from pandas import DataFrame
from scipy.optimize import curve_fit

plt.style.use(["paper", "onethirdpage"])

p = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
p.add_argument("path", help=".csv path")
p.add_argument(
    "--blim",
    default=20e-3,
    help="fit slope on the domain [-blim, blim]",
)
p.add_argument(
    "--quiet",
    help="suppress plots and console output",
    action="store_true",
)
args = p.parse_args()
outdir = Path(args.path).parent / Path(__file__).stem
outdir.mkdir(exist_ok=True)

df = pd.read_csv(args.path)
bfield = df.iloc[:, 0]
(gate_col,) = [c for c in df.columns if "gate" in c]
(gate,) = df[gate_col].unique()
mask = (-args.blim <= bfield) & (bfield <= args.blim)


def model(x, m, b):
    return m * x + b


def fit(column):
    y = df[column]
    yerr = df[column + "_err"]
    popt, pcov = curve_fit(
        model, bfield[mask], y[mask], sigma=yerr[mask], absolute_sigma=True
    )
    return popt, pcov


def plot(
    df,
    y_col,
    popt,
    *,
    xunit=1e-3,
    yunit,
    xlabel="$B_\parallel$ (mT)",
    ylabel,
    title=r"$V_\mathrm{g}=" f"{gate}\,$V",
):
    fig, ax = plt.subplots()
    fig.set_figheight(fig.get_figwidth())
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    y = df[y_col]
    yerr = df[f"{y_col}_err"]
    line = ax.errorbar(
        bfield[mask] / xunit,
        y[mask] / yunit,
        yerr=yerr[mask] / yunit,
        ls="none",
        marker="o",
        label="data (included in fit)",
    )[0]
    ax.errorbar(
        bfield[~mask] / xunit,
        y[~mask] / yunit,
        yerr=yerr[~mask] / yunit,
        ls="none",
        marker="o",
        mfc="w",
        color=line.get_color(),
        label="data (excluded from fit)",
    )
    ax.plot(bfield / xunit, model(bfield, *popt) / yunit, label="fit")
    ax.legend()
    fig.savefig(outdir / f"fit_{y_col}.png")


fit_delta = fit("delta")
fit_eta = fit("eta")
plot(df, "delta", fit_delta[0], yunit=1e-9, ylabel=r"$\Delta I_\mathrm{c}$ (nA)")
plot(df, "eta", fit_eta[0], yunit=1 / 100, ylabel=r"$\eta$ (%)")

# save fit parameters
df = {"gate": gate}
for y in "delta", "eta":
    popt, pcov = vars()[f"fit_{y}"]
    for name, val, err in zip(("slope", "yint"), popt, np.sqrt(np.diag(pcov))):
        df[f"{y}_{name}"] = [val]
        df[f"{y}_{name}_err"] = [err]
df = DataFrame({**df, **{k: [v] for k, v in args.__dict__.items()}})
df.to_csv(outdir / "fit.csv", index=False)

if not args.quiet:
    plt.show()
