#!/bin/bash

# Usage:
#   (bash bulk-postprocess.sh > >(tee logs/stdout.log) 2> >(tee logs/stderr.log >&2)) &> >(tee logs/stdall.log)    

# Invert current to conform to sign convention
find "../data/processed/centermax" -type f \
  -regex '.*Wsc=0\.\(3um-N\|6um-NNW\|9um-NNE_WFS06\)_.*/data.csv' \
  | xargs python invert_current.py

# Compute diode
find ../data/processed -type f -path */JS633-W2*/*/data.csv -exec \
  python compute_diode.py {} \;

# zero-field slope data
declare -a datasets=(
  "JS633-W2_Wsc=0.9um-ENE_WFS06_slopes"
  "JS633-W2_Wsc=0.9um-ENE_WFS06_slopes+10Vreset"
  "JS633-W2_Wsc=0.9um-NNE_WFS06_slopes"
  "JS633-W2_Wsc=0.9um-NNE_WFS07_slopes"
)
for ds in "${datasets[@]}"
do
  echo "Concatenating slope data... ($ds)"
  find "../data/processed/centermax/${ds}" -type f -path */diode-lowfield*/data.csv | xargs \
    python concat_csvs.py -f --output_filename='data_concat.csv' \
      --rename 'gate 21 - Source voltage' --to 'gate' \
      --rename 'gate 15 - Source voltage' --to 'gate' \
      --rename 'gate - Source voltage' --to 'gate' \
      --rename 'VectorMagnet - Field Z' --to 'field' \
      --rename 'VectorMagnet - Field Y' --to 'field' \
      --rename 'in-plane magnitude' --to 'field'
  echo ...fitting slopes...
  find "../data/processed/centermax/${ds}" -type f -path */diode-lowfield*/data.csv -exec \
    python fit_slope.py --quiet {} \;
  echo ...concatenating fits...
  find "../data/processed/centermax/${ds}" -type f -path */fit_slope/fit.csv | xargs \
    python concat_csvs.py -f --output_filename='slopes.csv'
  echo ...fitting slope data for B*...
  find "../data/processed/centermax/${ds}" -type f -path */diode-lowfield*/data.csv -exec \
    python $SHABANIPY_SCRIPTS/jj/fit_diode.py {} \
      --quiet \
      --remove-zero-field-offset \
      --icp_err_col=rmse+ \
      --icm_err_col=rmse- \
      \;
  echo ...concatenating B* fits...
  find "../data/processed/centermax/${ds}" -type f -path */fit_diode/data_fit.csv | xargs \
    python concat_csvs.py -f --output_filename='bstar.csv'
  python unpack_filename.py "../data/processed/centermax/${ds}/bstar.csv"
done
echo ...deduplicating slope data and fits...
python dedupe_slopes.py
echo ...done

# 20mT angle-dependence data
ROOT='../data/processed/centermax/JS633-W2'
REGEX='.*diode-angle_20mT_-?[0-9]\.[0-9]+V'
FILENAME='data'
echo Concatenating angle-dependence data...
find -E "$ROOT" -type f -regex "$REGEX/$FILENAME.csv" \
  | xargs python concat_csvs.py -f \
  --output_filename='data_angle.csv' \
  --rename 'gate - Source voltage' --to 'gate'
echo ...deduping...
python dedupe_angles.py
echo ...fitting...
find -E "$ROOT" -type f -regex "$REGEX/$FILENAME.csv" \
  -exec python fit_angle_dependence.py {} --quiet \;
echo ...concatenating fits...
find -E "$ROOT" -type f -regex "$REGEX/fit_angle_dependence/${FILENAME}_fit.csv" \
  | xargs python concat_csvs.py -f --output_filename='anglefits.csv'
echo ...done
