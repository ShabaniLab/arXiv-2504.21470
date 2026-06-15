#!/bin/bash
#
# source this script to set up environment

export PYTHONPATH=~/repos/shabanipy:$PYTHONPATH
export LABBERDATA_DIR=~/repos/arXiv-2504.21470/data/raw
export SHABANIPY_OUTPUT_DIR=~/repos/arXiv-2504.21470/data/processed
mkdir -p $SHABANIPY_OUTPUT_DIR
export SHABANIPY_SCRIPTS=~/repos/shabanipy/scripts/
export MPLCONFIGDIR=~/repos/shabanipy/shabanipy/utils/plotting/
