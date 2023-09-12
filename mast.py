import matplotlib.pyplot as plt
import argparse
import os
import time
import sys
import numpy as np
from uncertainties import unumpy
from astroquery.mast import Observations
from coordinates import convert_ra_dec
from fetch_lc import create_outdir, get_source_names

ap = argparse.ArgumentParser(description='Fetch data from MAST (HST, Swift-UVOT, GALEX and SPITZER)')
ap.add_argument("--ra", help="Right ascension", type=str, nargs="?", required=True)
ap.add_argument("--dec", help="Declination", type=str, nargs="?", required=True)
ap.add_argument("-o", "--outdir", nargs='?', help="Output dir name", type=str, default="data")
args = ap.parse_args()

ra = args.ra
dec = args.dec
outdir = args.outdir

ra, dec = convert_ra_dec(ra, dec)
source_name = get_source_names(ra, dec)[0]

ra_dec = "%.12f %+.12f" % (ra, dec)
print("(RA, Dec) = (%s)" % (ra_dec))

if not os.path.isdir(outdir):
    os.mkdir(outdir)

outdir = create_outdir(outdir, source_name)

obs_table = Observations.query_region("%.5f, %+.5f" % (ra, dec))
# get only lcs
lcs = obs_table[obs_table["dataproduct_type"]=="timeseries"]

if len(lcs) == 0:
    print("No data found")

else:
    print("Data found:------\n")
    print(lcs)
    missions =["GALEX", "SWIFT", "SPITZER_SHA"] # , "HST" gives weird results, things that are not lightcurves actually
    # galex
    for mission in missions:
        lcs_mission = lcs[lcs["obs_collection"]==mission]
        if len(lcs_mission)==0:
            print("No data found for %s" % mission)
        else:
            print("%d obs found for %s" % (len(lcs_mission), mission))
            mission_data = Observations.get_product_list(lcs_mission)
            manifest = Observations.download_products(mission_data, productType="SCIENCE", download_dir=outdir)
            print(manifest)
