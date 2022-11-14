import matplotlib.pyplot as plt
import argparse
import os
import time
import sys
from ztfquery import lightcurve
import numpy as np
from uncertainties.umath import log10 as ulog
from uncertainties import ufloat
from uncertainties import unumpy
from astroquery.mast import Observations
from coordinates import convert_ra_dec
# https://www.ptf.caltech.edu/page/lcgui
ap = argparse.ArgumentParser(description='Fetch data from ZTF https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html')
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

obs_table = Observations.query_region("%.5f, %+.5f" % (ra, dec)) 
# get only lcs
lcs = obs_table[obs_table["dataproduct_type"]=="timeseries"]

if len(lcs) == 0:
    print("No data found")
else:
    missions =["GALEX", "SWIFT", "SPITZER_SHA", "HST"]
    # galex
    for mission in missions:
        lcs_mission = lcs[lcs["obs_collection"]==mission]
        if len(lcs_mission)==0:
            print("No data found for %s" % mission)
        else:
            print("%d obs found for %s" % (len(lcs_mission), mission))
            mission_dir = "%s/%s" %(outdir, mission)
            if not os.path.isdir(mission_dir):
                os.mkdir(mission_dir)
            mission_data = Observations.get_product_list(lcs_mission)
            manifest = Observations.download_products(mission_data, productType="SCIENCE", download_dir=mission_dir)
            print(manifest)
