import matplotlib.pyplot as plt
import argparse
import os
import time
import sys
import lightkurve as lk
import numpy as np
from uncertainties import ufloat
from uncertainties import unumpy
import math as m
from coordinates import convert_ra_dec
import warnings
from fetch_lc import get_source_names, create_outdir

zero_point = ufloat(20.44, 0.05)

ap = argparse.ArgumentParser(description='Fetch data from TESS, K2 and Kepler')
ap.add_argument("--ra", help="Right ascension", type=str, nargs="?", required=True)
ap.add_argument("--dec", help="Declination", type=str, nargs="?", required=True)
ap.add_argument("-o", "--outdir", nargs='?', help="Output dir name", type=str, default="data")
args = ap.parse_args()

if not os.path.isdir("data"):
    os.mkdir("data")


ra_str = args.ra
dec_str = args.dec
outdir = args.outdir
if not os.path.isdir(outdir):
    os.mkdir(outdir)

ra, dec = convert_ra_dec(ra_str, dec_str)

ra_dec = "%.12f %+.12f" % (ra, dec)

names = get_source_names(ra, dec)

outdir = create_outdir(outdir, names[0])

header = "t_day\tflux\tflux_err\texposure\tbkg_rate\tbkg_err\tmag\tmag_err"

search_result = lk.search_lightcurve('%s' % (ra_dec), radius=0.1, mission=('Kepler', 'K2', 'TESS'),
                   author=("K2", "Kepler", "TESS", "SPOC")) # 0.0001 is the default in arcsec #TESS-SPOC might give more up-todate lightcurves
if len(search_result) == 0:
    print(search_result)
else:
    print(search_result)
    lc_collection = search_result.download_all()
    # Plot Kepler Lightcurves
    fig, ax = plt.subplots(figsize=(20,5))
    for i, lc in enumerate(lc_collection):
        object_name = lc.meta["LABEL"]
        if object_name not in names:
            warnings.warn("Object %s is not in the list of main IDs:" % object_name)
            print(names)

        else:
            print("Object %s found in list" % object_name)
        lc.normalize().plot(ax=ax, label="%s" %(lc.meta["MISSION"]))
        outputfile = "%s/%s_%i.dat" %(outdir, lc.meta["MISSION"], i)
        mask = (lc.quality == 0) & (lc.flux.value >0)
        flux = unumpy.uarray(lc.flux.value[mask], lc.flux_err.value[mask])
        #mask = lc.flux > 0
        mag = -2.5 * unumpy.log10(flux) + zero_point
        # timedel is in days https://archive.stsci.edu/missions/tess/doc/EXP-TESS-ARC-ICD-TM-0014.pdf#page=32
        dt_sec = lc.meta["TIMEDEL"] * 24 * 3600
        np.savetxt(outputfile, np.asarray([lc.time.value[mask], lc.flux[mask], lc.flux_err[mask], dt_sec * np.ones(len(mag)), lc.sap_bkg[mask], lc.sap_bkg_err[mask],
                    unumpy.nominal_values(mag), unumpy.std_devs(mag)]).T,
                   delimiter="\t", fmt="%.6f", header=header)
        # 1h binned lightcurves
        dt_day = 1 / 24
        rebinned_dt_sec = dt_day * 24 * 3600
        rebinned = lc.bin(dt_day)
        mask = (rebinned.quality == 0) & (rebinned.flux.value >0)
        flux = unumpy.uarray(rebinned.flux.value[mask], rebinned.flux_err.value[mask])
        #mask = lc.flux > 0
        mag = -2.5 * unumpy.log10(flux) + zero_point
        outputfile = "%s/%s_%i_1h.dat" %(outdir, lc.meta["MISSION"], i)
        np.savetxt(outputfile, np.asarray([rebinned.time.value[mask], rebinned.flux[mask], rebinned.flux_err[mask],
                    rebinned_dt_sec * np.ones(len(mag)), rebinned.sap_bkg[mask], rebinned.sap_bkg_err[mask],
                    unumpy.nominal_values(mag), unumpy.std_devs(mag)]).T,
                   delimiter="\t", fmt="%.6f", header=header)

    ax.legend()

    plt.savefig("%s/tess.png" % outdir)
