import matplotlib.pyplot as plt
import argparse
import os
import time
import sys
import lightkurve as lk
import numpy as np
from uncertainties.umath import log10 as ulog
from uncertainties import ufloat
from uncertainties import unumpy
import math as m
from coordinates import convert_ra_dec
from astroquery.simbad import Simbad

ap = argparse.ArgumentParser(description='Fetch data from TESS, K2 and Kepler')
ap.add_argument("--ra", help="Right ascension", type=str, nargs="?", required=True)
ap.add_argument("--dec", help="Declination", type=str, nargs="?", required=True)
ap.add_argument("-o", "--outdir", nargs='?', help="Output dir name", type=str, default="data")
args = ap.parse_args()

zero_point = ufloat(20.44, 0.05)

ra = args.ra
dec = args.dec
outdir = args.outdir

ra, dec = convert_ra_dec(ra, dec)

ra_dec = "%.12f %+.12f" % (ra, dec)
print("(RA, Dec) = (%s)" % (ra_dec))

if not os.path.isdir(outdir):
    os.mkdir(outdir)
## KEPLER data

result_table = Simbad.query_region("%.5f, %+.5f" % (ra, dec))
name = result_table[0]["MAIN_ID"]
print("Source name\n ------ \n %s" % name)
outdir += "/%s" % name

if not os.path.isdir(outdir):
    os.mkdir(outdir)

search_result = lk.search_lightcurve('%s' % (ra_dec), radius=0.01 * 3600, mission=('Kepler', 'K2', 'TESS'),
                   author=("K2", "Kepler", "TESS", "SPOC")) # 0.0001 is the default in arcsec
if len(search_result) == 0:
    print(search_result)
else:
    print(search_result)
    lc_collection = search_result.download_all()
    # Plot Kepler Lightcurves
    fig, ax = plt.subplots(figsize=(20,5))
    for i, lc in enumerate(lc_collection):
        lc.normalize().plot(ax=ax, label="%s" %(lc.meta["MISSION"]))
        outputfile = "%s/%s_%i.dat" %(outdir, lc.meta["MISSION"], i)
        flux = unumpy.uarray(lc.flux.value, lc.flux_err.value)
        mag = -2.5 * unumpy.log10(flux) + zero_point
        np.savetxt(outputfile, np.asarray([lc.time.value, unumpy.nominal_values(mag), unumpy.std_devs(mag)]).T,
                   delimiter="\t", fmt="%.6f", header="t\tmag\terr")
    ax.legend()
    plt.savefig("%s/tess.png" % outdir)
