import matplotlib.pyplot as plt
import argparse
import os
import time
import numpy as np
from coordinates import convert_ra_dec
from astroquery.simbad import Simbad
import pyvo


ap = argparse.ArgumentParser(description='Fetch data from WISE multi-epoch catalog https://wise2.ipac.caltech.edu/docs/release/allwise/expsup/sec3_1a.html')
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

# WISE data from the
url = "https://irsa.ipac.caltech.edu/SCS?table=allwise_p3as_mep"
objects = pyvo.conesearch(url, pos=(ra, dec), radius = 1 / 3600) # radius in degrees
unique_ids = np.unique(objects["source_id_mf"])
print("Found %d unique objects" % len(unique_ids))
bands = ["w1", "w2", "w3", "w4"]
for unique in unique_ids:
    data = objects.to_table()[objects["source_id_mf"]==unique]
    for band in bands:
        plt.errorbar(data["mjd"], data["%smpro_ep" % band],
        yerr=data["%ssigmpro_ep" % band], label="%s" % band, ls="None")
        data.write('%s/wise_%s.dat' % (outdir, band), format='csv', overwrite=True)

plt.legend()
plt.xlabel("MJD")
plt.ylabel("WISE magnitude")
plt.savefig("%s/wise.png" % (outdir))
