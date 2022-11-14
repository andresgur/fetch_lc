import matplotlib.pyplot as plt
import argparse
import os
import time
import numpy as np
from uncertainties import unumpy
import math as m
from coordinates import convert_ra_dec
from astroquery.simbad import Simbad
from astroquery.ipac.irsa import Irsa
import warnings

ap = argparse.ArgumentParser(description='Fetch data from PFT (https://www.ptf.caltech.edu/system/media_files/binaries/30/original/Objects_SourcesTable_cols_v3.html)')
ap.add_argument("--ra", help="Right ascension", type=str, nargs="?", required=True)
ap.add_argument("--dec", help="Declination", type=str, nargs="?", required=True)
ap.add_argument("-o", "--outdir", nargs='?', help="Output dir name", type=str, default="data")
args = ap.parse_args()

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

# PTF data from the
lightcurves = Irsa.query_region("%.5f, %+.5f" % (ra, dec), catalog="ptf_lightcurves", radius='0.4"') # in arcsec
unique_ids = np.unique(lightcurves["oid"])
print("Found %d unique objects \n" % (len(unique_ids)))
print(unique_ids)
bands = [1, 2] # (1 = g; 2 = R).
bandnames = ["g", "R"]
n_unique_ids = len(unique_ids)
if n_unique_ids!=0:

    for index, unique in enumerate(unique_ids):
        data = lightcurves[lightcurves["oid"]==unique]
        for band, bandname in zip(bands, bandnames):
            data_band = data[data["fid"]==band]
            if len(data_band) == 0:
                warnings.warn("No data for filter %s" % bandname)
            plt.errorbar(data_band["obsmjd"], data_band["mag_autocorr"], yerr=data_band["magerr_auto"],
                         ls="None", label="PTF%s_%d" % (bandname, index))
            outputfile = '%s/ptf_%s_%d.dat' % (outdir, bandname, index)
            np.savetxt(outputfile, np.asarray([data_band["obsmjd"], data_band["mag_autocorr"],
                       data_band["magerr_auto"]]).T, delimiter="\t", fmt="%.6f", header="t\tmag\terr")

    plt.legend()
    plt.xlabel("MJD")
    plt.ylabel("PTF magnitude")
    plt.savefig("%s/ptf.png" % (outdir))
