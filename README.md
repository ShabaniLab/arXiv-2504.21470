# arXiv:2504.21470
[![DOI](https://zenodo.org/badge/1267749121.svg)](https://doi.org/10.5281/zenodo.20707782)

Figures and analysis for [arXiv:2504.21470](https://arxiv.org/abs/2504.21470)

## Running the data analysis

1. `clone` this repository and
   [shabanipy](https://github.com/shabanilab/shabanipy):

   ```bash
   mkdir ~/repos
   git clone https://github.com/ShabaniLab/arXiv-2504.21470.git ~/repos/arXiv-2504.21470
   git clone --revision=c9d29185dda34c697a36a4dc467895f9c3a52279 https://github.com/ShabaniLab/shabanipy.git ~/repos/shabanipy
   ```

2. Download the raw data files from
   [10.5281/zenodo.20672018](https://doi.org/10.5281/zenodo.20672018),
   unzip and move to the right location:

   ```bash
   unzip ~/downloads/data.zip
   mv data ~/repos/arXiv-2504.21470/data/raw
   ```

3. Set up environment:

   ```bash
   source ~/repos/arXiv-2504.21470/scripts/env.sh
   conda env create -f ~/repos/arXiv-2504.21470/conda-env.yaml -n arXiv-2504.21470
   conda activate arXiv-2504.21470
   ```

   Alternatively, `conda-env-from-history.yaml`, generated via
   `conda env export --from-history`,
   lists only the packages that were explicitly requested.

4. Run the scripts in `figures/` to reproduce the figures.

5. The data analysis can be reproduced by running the bulk data processing
   scripts.  The following invocation will produce log files while printing
   output to the console.  (The raw data analysis will take a very long
   time...)

   ```bash
   cd ~/repos/arXiv-2504.21470/scripts
   mkdir logs
   (bash bulk-process-raw-data.sh > >(tee logs/stdout.log) 2> >(tee logs/stderr.log >&2)) &> >(tee logs/stdall.log)
   bash bulk-postprocess.sh
   ```

   N.b. these bulk processing scripts have not been rigorously tested.  YMMV.
