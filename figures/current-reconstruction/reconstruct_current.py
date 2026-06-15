"""Reconstruct critical current distribution from Fraunhofer interference pattern."""
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from scipy.constants import physical_constants
from shabanipy.dvdi import extract_switching_current
from shabanipy.jj import extract_current_distribution, recenter_fraunhofer
from shabanipy.labber import ShaBlabberFile
from shabanipy.utils import jy_pink, load_config, plot, plot2d

BPERP_LABEL = r"$B_\perp$ (mT)"

jy_pink.register()
plt.style.use(["paper", "fullcolumn", "jy_pink"])
outdir = Path(__file__).parent / "plots"
outdir.mkdir(parents=True, exist_ok=True)

ini, _ = load_config("config.ini")
for config_section in ini.sections():
    _, config = load_config("config.ini", config_section)
    width = config.getfloat("JJ_WIDTH")
    length = config.getfloat("JJ_LENGTH")
    datapath = Path(config["DATAPATH"])

    filters = []
    if config.getfloat("FIELD_MIN"):
        filters.append(
            (config["CH_FIELD_PERP"], np.greater, config.getfloat("FIELD_MIN"))
        )
    if config.getfloat("FIELD_MAX"):
        filters.append((config["CH_FIELD_PERP"], np.less, config.getfloat("FIELD_MAX")))

    # load the data
    with ShaBlabberFile(datapath) as f:
        bfield, ibias, volts = f.get_data(
            config["CH_FIELD_PERP"],
            config["CH_BIAS"],
            config["CH_MEAS"],
            order=(config["CH_FIELD_PERP"], config["CH_BIAS"]),
            filters=filters,
        )
        volts /= config.getfloat("DC_AMP_GAIN")
        dvdi = np.gradient(volts, axis=-1) / np.gradient(ibias, axis=-1)
        gate = f.get_fixed_value(config["CH_GATE"])

    GATE_TITLE = f"$V_\\text{{g}}={gate}$ V"

    # plot the raw data
    fig, ax = plot2d(
        bfield / 1e-3,
        ibias / 1e-6,
        dvdi,
        xlabel=BPERP_LABEL,
        ylabel=r"$I_\text{bias}$ (μA)",
        zlabel="$dV/dI$ (Ω)",
        title=GATE_TITLE,
        vmin=config.getfloat("VMIN"),
        vmax=config.getfloat("VMAX"),
        extend_min=False,
    )
    fig.savefig(outdir / f"{config_section}_fraunhofer.png")

    # extract the switching current
    bfield = np.unique(bfield)
    ic = extract_switching_current(
        ibias,
        volts,
        threshold=config.getfloat("THRESHOLD"),
        interp=True,
        offset_npoints=5,
    )
    plot(bfield / 1e-3, ic / 1e-6, ax=ax, color="k", lw=1)
    fig.savefig(outdir / f"{config_section}_ic-extraction.png")

    # center fraunhofer
    bfield = recenter_fraunhofer(bfield, ic)
    fig, ax = plt.subplots()
    ax.axvline(0, color="k")
    plot(
        bfield / 1e-3,
        ic / 1e-6,
        ax=ax,
        xlabel=BPERP_LABEL,
        ylabel=r"$I_\text{c}$ (μA)",
        title=GATE_TITLE,
    )
    ax.set_ylim((0, None))
    fig.savefig(outdir / f"{config_section}_ic-centered.png")

    PHI0 = physical_constants["mag. flux quantum"][0]
    FIELD_TO_WAVENUM = 2 * np.pi * length / PHI0
    x, jx = extract_current_distribution(
        bfield, ic, FIELD_TO_WAVENUM, width, len(bfield)
    )
    fig, ax = plt.subplots(constrained_layout=True)
    ax.set_xlabel(r"$x$ (μm)")
    ax.set_ylabel(r"$J_\text{c}(x)$ (μA/μm)")
    ax.axhline(0, color="k")
    ax.plot(x * 1e6, jx)
    ax.fill_between(x * 1e6, jx, alpha=0.5)
    ax.set_title(GATE_TITLE)
    fig.savefig(outdir / f"{config_section}_current-density.png")

# plt.show()
