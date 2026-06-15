from itertools import product

import pandas as pd
from matplotlib import pyplot as plt

plt.style.use(["paper", "fullcolumn"])
arrowlabel = {0: r"$\leftarrow$", 1: r"$\rightarrow$"}

fig, axs = plt.subplots(nrows=2, sharex=True)
fig.set_figheight(1.5 * fig.get_figheight())
axs[-1].set_xlabel(r"$V_\text{g}$ (V)")
for ax in axs:
    ax.set_ylabel(r"$I_\mathrm{c}$ (μA)")
    ax.axhline(0, color="grey", lw=0.5)

# NNE
ax = axs[0]
csv = pd.read_csv("hysteresis_NNE1_ic.csv")
csv.fillna(0, inplace=True)
repeat = 1
for increasing in (0, 1):
    mask = (csv["repeat"] == repeat) & (csv["Vg increasing"] == increasing)
    (line,) = ax.plot(
        csv[mask]["gate 15 - Source voltage"],
        csv[mask]["ic+"] / 1e-6,
        ".-",
        ms=2,
        lw=0.5,
        label=f"{arrowlabel[increasing]} sweep {repeat}",
    )
    ax.plot(
        csv[mask]["gate 15 - Source voltage"],
        csv[mask]["ic-"] / 1e-6,
        ".-",
        ms=2,
        lw=0.5,
        color=line.get_color(),
    )
csv = pd.read_csv("hysteresis_NNE2_ic.csv")
csv.fillna(0, inplace=True)
repeat = 2
for increasing in (0, 1):
    mask = csv["Vg increasing"] == increasing
    (line,) = ax.plot(
        csv[mask]["gate 15 - Source voltage"],
        csv[mask]["ic+"] / 1e-6,
        ".-",
        ms=2,
        lw=0.5,
        label=f"{arrowlabel[increasing]} sweep {repeat}",
    )
    ax.plot(
        csv[mask]["gate 15 - Source voltage"],
        csv[mask]["ic-"] / 1e-6,
        ".-",
        ms=2,
        lw=0.5,
        color=line.get_color(),
    )
legend = ax.legend(fontsize="xx-small", title="Device A", title_fontsize="xx-small")

# ENE
ax = axs[1]
csv = pd.read_csv("hysteresis_ENE_ic.csv")
csv.fillna(0, inplace=True)
for repeat, increasing in product((1, 2), (0, 1)):
    mask = (csv["repeat"] == repeat) & (csv["Vg increasing"] == increasing)
    (line,) = ax.plot(
        csv[mask]["gate 21 - Source voltage"],
        csv[mask]["ic+"] / 1e-6,
        ".-",
        ms=2,
        lw=0.5,
        label=f"{arrowlabel[increasing]} sweep {repeat}",
    )
    ax.plot(
        csv[mask]["gate 21 - Source voltage"],
        csv[mask]["ic-"] / 1e-6,
        ".-",
        ms=2,
        lw=0.5,
        color=line.get_color(),
    )
legend = ax.legend(fontsize="xx-small", title="Device B", title_fontsize="xx-small")

fig.savefig("hysteresis.svg")
