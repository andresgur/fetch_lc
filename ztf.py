import matplotlib.pyplot as plt
import argparse
import os
import time
import sys
from ztfquery import lightcurve
import numpy as np
from uncertainties.umath import log10 as ulog
from uncertainties import unumpy
from coordinates import convert_ra_dec
from fetch_lc import create_outdir, get_source_names

# https://www.ptf.caltech.edu/page/lcgui
ap = argparse.ArgumentParser(description='Fetch data from ZTF https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html')
ap.add_argument("--ra", help="Right ascension", type=str, nargs="?", required=True)
ap.add_argument("--dec", help="Declination", type=str, nargs="?", required=True)
ap.add_argument("-o", "--outdir", nargs='?', help="Output dir name", type=str, default="data")
args = ap.parse_args()

if not os.path.isdir("data"):
    os.mkdir("data")

ra = args.ra
dec = args.dec
outdir = args.outdir

ra, dec = convert_ra_dec(ra, dec)

ra_dec = "%.12f %+.12f" % (ra, dec)
print("(RA, Dec) = (%s)" % (ra_dec))

if not os.path.isdir(outdir):
    os.mkdir(outdir)

name = get_source_names(ra, dec)[0]
outdir = create_outdir(outdir, name)

lcq = lightcurve.LCQuery.from_position(ra, dec, 5) # radius in arcsec

if len(lcq.data) == 0:
    print("No data found")
else:

    data = lcq.data
    print("Found %d ZTF observations" % len(lcq.data))
    # Plot Kepler Lightcurves
    fig, ax = plt.subplots()

    bands = ["zg", "zr", "zi"]
    for band in bands:
        # sometimes the data is not sorted, so let's sort it
        band_data = data[data["filtercode"].values==band]
        times = band_data['mjd'].values
        mags = band_data['mag'].values
        mag_err = band_data['magerr'].values
        exptime = band_data["exptime"].values
        magzp = band_data["magzp"].values # zero points
        catflags = band_data["catflags"].values
        flux = 10**((band_data["mag"] + magzp).values / (-2.5))
        dflux = np.log(10) * flux / (2.5) * (np.sqrt(band_data["magerr"]**2).values) # adding back in the error on zpmag would be double counting as presumably magerr already has that band_data["magzprms"]**2

        plt.errorbar(times, mags, yerr=mag_err,
                     ls='None', label="%s" % band) # , fmt="+"
        outputfile = "%s/ztf_%s.dat" %(outdir, band)
        np.savetxt(outputfile, np.asarray([times, mags, mag_err,exptime, flux, dflux, magzp, catflags]).T,
                   fmt="%.6f\t%.5f\t%.5f\t%.1f\t%.5e\t%.5e\t%.4f\t%d", header="t\tmag\terr\texposures\tflux\tdflux\tmagzp\tcatflags")
    ax.legend()
    plt.savefig("%s/ztf.png" % outdir)
