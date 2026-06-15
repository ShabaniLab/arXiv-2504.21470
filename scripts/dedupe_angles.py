"""Dedupe angle-dependence data e.g. for pcolormesh plots.

One angle (θz=0) at one gate voltage (-2.4V) was repeated (WFS07-030 and WFS07-031) with
different current-bias step sizes.  The difference is negligible; choose the one with
the lowest average RMS.
"""
import pandas as pd

path = "../data/processed/centermax/JS633-W2/data_angle.csv"
df = pd.read_csv(path)

cp = df.copy()
cp["mean_rmse"] = cp[["rmse+", "rmse-"]].mean(axis=1)
grouped = cp.groupby(["gate", "angle-from-z"])
cp["min_mean_rmse"] = cp.groupby(["gate", "angle-from-z"])["mean_rmse"].transform(
    lambda s: s.min()
)
drop = cp[cp["mean_rmse"] != cp["min_mean_rmse"]]

df.drop(drop.index, inplace=True)
df.to_csv(path, index=False)
