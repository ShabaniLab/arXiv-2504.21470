"""Dedupe slope data w.r.t. Vg for e.g. pcolormesh plots."""
from pathlib import Path

import numpy as np
from pandas import read_csv

dataset_dirs = (
    "JS633-W2_Wsc=0.9um-ENE_WFS06_slopes",
    "JS633-W2_Wsc=0.9um-ENE_WFS06_slopes+10Vreset",
    "JS633-W2_Wsc=0.9um-NNE_WFS06_slopes",
    "JS633-W2_Wsc=0.9um-NNE_WFS07_slopes",
)
datapaths = [
    Path(f"../data/processed/centermax/{dir_}/data_concat.csv") for dir_ in dataset_dirs
]
slopepaths = [
    Path(f"../data/processed/centermax/{dir_}/slopes.csv") for dir_ in dataset_dirs
]
bstarpaths = [
    Path(f"../data/processed/centermax/{dir_}/bstar.csv") for dir_ in dataset_dirs
]
groupcols = ["gate", "parent_csv"]

for dpath, spath, bpath in zip(datapaths, slopepaths, bstarpaths):
    df = read_csv(dpath)
    sf = read_csv(spath)
    bf = read_csv(bpath)

    # remove scans that have fewer points
    grouped = df.groupby(groupcols)["field"]
    count = grouped.count()
    drop = count[count < count.max()]
    for index in drop.index.values:
        df.drop(grouped.get_group(index).index, inplace=True)
        for dff in sf, bf:
            dff.drop(
                dff[
                    (dff["gate"] == index[0])
                    & (
                        dff["parent_csv"].apply(lambda p: Path(p).parent.parent)
                        == Path(index[1]).parent
                    )
                ].index,
                inplace=True,
            )

    # remove duplicate gates with higher average delta_err
    cp = df.copy()
    cp["mean_delta_err"] = cp.groupby(groupcols)["delta_err"].transform(
        lambda s: np.mean(s)
    )
    cp["minmean_delta_err"] = cp.groupby("gate")["mean_delta_err"].transform("min")
    drop = cp[cp["mean_delta_err"] != cp["minmean_delta_err"]]
    df.drop(drop.index, inplace=True)
    for index in drop.groupby(groupcols).count().index.values:
        for dff in sf, bf:
            dff.drop(
                dff[
                    (dff["gate"] == index[0])
                    & (
                        dff["parent_csv"].apply(lambda p: Path(p).parent.parent)
                        == Path(index[1]).parent
                    )
                ].index,
                inplace=True,
            )

    df.to_csv(dpath.parent / "data_deduped.csv", index=False)
    sf.to_csv(spath.parent / "slopes_deduped.csv", index=False)
    bf.to_csv(spath.parent / "bstar_deduped.csv", index=False)
