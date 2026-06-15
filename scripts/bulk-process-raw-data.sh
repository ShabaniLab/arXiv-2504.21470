#!/bin/bash

# Usage:
#   (bash bulk-process-raw-data.sh > >(tee logs/stdout.log) 2> >(tee logs/stderr.log >&2)) &> >(tee logs/stdall.log)    

#set -x # print commands as they're executed
#set -e # exit script if a command fails

pushd ~/repos/shabanipy/scripts/jj/fraunhofer
centermax_sections_matching () {
  local regex=$1
  local config=$2
  \grep \\[$regex\\] $config | while read -r section;
  do 
    python -u centermax.py -f $config ${section:1:-1}
  done
}
# Wsc=0.9um (ENE and NNE) slopes and angle dependence
centermax_sections_matching 'diode.*' "configs/JS633-W2_Wsc=0.9um-ENE_WFS06_slopes.ini"
centermax_sections_matching 'diode.*' "configs/JS633-W2_Wsc=0.9um-ENE_WFS06_slopes+10Vreset.ini"
centermax_sections_matching 'diode.*' "configs/JS633-W2_Wsc=0.9um-NNE_WFS06_slopes.ini"
centermax_sections_matching 'diode.*' "configs/JS633-W2_Wsc=0.9um-NNE_WFS07_slopes.ini"
centermax_sections_matching '.*diode-angle_20mT.*' "configs/JS633-W2.ini"
popd
