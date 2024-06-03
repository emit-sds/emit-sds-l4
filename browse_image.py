


import argparse
import numpy as np
from netCDF4 import Dataset
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(description='netcdf conversion')
    parser.add_argument('input_rf_file', type=str)
    parser.add_argument('output_file', type=str)
    args = parser.parse_args()


    ds = Dataset(args.input_rf_file, 'r')

    if len(ds.variables['dust_lw_rf_toa'].shape) == 4:
        dust_lw_rf_toa = np.sum(np.array(ds.variables['dust_lw_rf_toa'][...]),axis=0)
    elif len(ds.variables['dust_lw_rf_toa'].shape) == 3:
        dust_lw_rf_toa = np.array(ds.variables['dust_lw_rf_toa'][...])

    mean_lw_rf = np.mean(dust_lw_rf_toa, axis=0)

    fig = plt.figure(figsize=(8, 4))
    plt.imshow(mean_lw_rf)
    plt.axis('off')
    plt.title('Mean Dust Longwave Radiative Forcing\nin Bin 0, TOA (W m$^{-2}$)')
    plt.colorbar()


    plt.savefig(args.output_file, dpi=300, bbox_inches='tight')






if __name__ == "__main__":
    main()

