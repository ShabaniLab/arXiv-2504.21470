import numpy as np
from matplotlib import pyplot as plt


def lifshitz(α, β1, β3, current="110"):
    """q^3 Lifshitz invariant in GL free energy responsible for diode.

    βj > 0 assumed.  βj → -βj when `current="1-10"`.
    """
    if current == "110":
        pass
    elif current == "1-10":
        β1 *= -1
        β3 *= -1
    else:
        raise ValueError(f"I don't recognize {current=}")

    return (
        (α - β1) * (α + β1) ** 2
        - 3 * (α - β1) * (α + β1) * β3
        + (6 * α + 2 * β1) * β3**2
        - 3 * β3**3
    )


β1 = 1
β3 = np.array([0, 0.25, 0.5]) * β1
α = np.linspace(-1.5, 1.5) * β1

plt.style.use(["paper"])
figsize = (2.33, 1.5)
fig1, ax1 = plt.subplots(figsize=figsize)
fig2, ax2 = plt.subplots(figsize=figsize)
axs = (ax1, ax2)
for ax in axs:
    ax.set_xlabel(r"$\alpha/\beta_1$", x=0.98, labelpad=-10)
    ax.set_ylabel(r"$F_\text{L}/h$", y=1.05, labelpad=-20, rotation=0)
    ax.axhline(0, color="grey", lw=0.5)
    ax.axvline(0, color="grey", lw=0.5)
    ax.spines[["left", "bottom"]].set_position(("data", 0))
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(top=False, right=False)

xtal = ("110", "1-10")
xtallabel = {
    "110": r"$I\parallel[110]$",
    "1-10": r"$I\parallel[1\overline{1}0]$",
}
for ax, xtal_ in zip(axs, xtal):
    ax.text(0, 1, xtallabel[xtal_], transform=ax.transAxes, ha="left", va="top")
    for β3_, color in zip(β3, ("k", "r", "b")):
        ax.plot(
            α / β1,
            lifshitz(α, β1=β1, β3=β3_, current=xtal_),
            label=r"$\beta_3/\beta_1=" f"{β3_:.3g}$",
            color=color,
        )
for ax in axs:
    ax.set_xlim((-1.5, 1.5))
    ax.set_ylim((-1.2, 1.2))
    ax.set_xticks([-1, 1])
    ax.set_yticks([-1, -0.5, 0.5, 1])
axs[1].legend(fontsize="xx-small", loc="lower right")
for fig, xtal_ in zip((fig1, fig2), xtal):
    fig.savefig(f"lifshitz_{xtal_}.svg", bbox_inches="tight")
