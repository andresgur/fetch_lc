import matplotlib.pyplot as plt
import argparse
import os
import time
import numpy as np
from coordinates import convert_ra_dec
import subprocess
from astroquery.simbad import Simbad
from coordinates import convert_ra_dec

ap = argparse.ArgumentParser(description='Fetch data from various archival data (so far TESS, PTF, ZTF, Swift-XRT, WISE)')
ap.add_argument("--ra", help="Right ascension", type=str, nargs="?", required=True)
ap.add_argument("--dec", help="Declination", type=str, nargs="?", required=True)
ap.add_argument("-o", "--outdir", nargs='?', help="Output dir name", type=str, default="data")
args = ap.parse_args()

ra = args.ra
dec = args.dec
ra, dec = convert_ra_dec(ra, dec)
result_table = Simbad.query_region("%.5f, %+.5f" % (ra, dec))
name = result_table[0]["MAIN_ID"]
print(" Source name\n --------- \n %s" % name)


archives = ["tess", "ptf", "ztf", "wise", "mast"] # "swift",

for archive in archives:
    print("Getting data from %s" % archive)
    p = subprocess.Popen("python %s.py --ra '%s' --dec '%s' -o %s" %(archive, ra, dec, args.outdir),
                         stdout=subprocess.PIPE, shell=True)
    out,err = p.communicate()
    print(out)

outdir = args.outdir
outdir += "/%s" % name
os.chdir(outdir)
p = subprocess.Popen("python ../../plot_data.py", stdout=subprocess.PIPE, shell=True)
out,err = p.communicate()
print(out)
print("Data stored to %s" % outdir)
