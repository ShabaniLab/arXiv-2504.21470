"""Fit diode efficiency η(θ) vs. angle."""
import argparse as ap
from pathlib import Path

import numpy as np
import pandas as pd
from lmfit import Model
from matplotlib import pyplot as plt
from matplotlib import rcParams
from pandas import DataFrame

# constrained_layout not compatible with lmfit's plotting methods
plt.style.use(["paper", "onethirdpage", {"figure.constrained_layout.use": False}])

p = ap.ArgumentParser(
    description=__doc__, formatter_class=ap.ArgumentDefaultsHelpFormatter
)
p.add_argument("datapath", help="path to .csv file")
p.add_argument(
    "--quiet",
    help="suppress plots and console output",
    action="store_true",
)
args = p.parse_args()

outdir = Path(args.datapath).parent / Path(__file__).stem
outdir.mkdir(exist_ok=True)
outpath = outdir / Path(args.datapath).stem


def threetheta_model(θ, a0, a1, a3, φ1, φ3):
    return a0 + a1 * np.sin(np.radians(θ + φ1)) + a3 * np.sin(np.radians(3 * θ + φ3))


df = pd.read_csv(args.datapath)
# measure angle from current (+90°) on domain [-π, π]
df["angle-from-I"] = ((((90 + df["angle-from-z"]) % 360) + 180) % 360) - 180

# fit
model = Model(threetheta_model)
params = model.make_params(
    a0=df["eta"].mean(),
    a1=(df["eta"].max() - df["eta"].min()) / 2,
    a3=0,
    φ1=0,
    φ3=0,
)
result = model.fit(
    df["eta"], θ=df["angle-from-I"], weights=1 / df["eta_err"], params=params
)

# save fit report
(gate,) = df["gate - Source voltage"].unique()
with open(str(outpath) + "_fit.txt", "w") as f:
    f.write(result.fit_report())

# plot fit results
fig = result.plot(
    show_init=False,
    title=f"$V_\mathrm{{g}}={gate}$ V",
    xlabel=r"$\theta$",
    ylabel=r"$\eta$",
    numpoints=100,
)
ax = fig.axes[-1]
ax.set_xticks([-180, -90, 0, 90, 180])
ax.set_xticklabels([r"$-\pi$", r"$-\frac{\pi}{2}$", "0", r"$\frac{\pi}{2}$", r"$\pi$"])
fig.tight_layout()
fig.savefig(str(outpath) + f"_fit.{rcParams['savefig.format']}")

# save fit parameters
fitparams = DataFrame(
    {
        "gate": df["gate - Source voltage"].unique(),
        **{k: [v] for k, v in result.best_values.items()},
        **{f"{k}_err": [v.stderr] for k, v in result.params.items()},
        **{k: [result.summary()[k]] for k in ("ndata", "chisqr", "redchi", "rsquared")},
        **{k: [v] for k, v in args.__dict__.items()},
    }
)
fitparams_filename = str(outpath) + "_fit.csv"
fitparams.to_csv(fitparams_filename, index=False)
print(f"Wrote {fitparams_filename}")

if not args.quiet:
    plt.show()
