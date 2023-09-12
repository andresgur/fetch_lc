import swifttools.ukssdc.xrt_prods as ux
import argparse
import os
import time
import sys
from coordinates import convert_ra_dec
from astroquery.simbad import Simbad
from fetch_lc import get_source_names, create_outdir

# https://www.swift.ac.uk/user_objects/API/RequestJob.md
ap = argparse.ArgumentParser(description='Fetch data from various Swift-XRT')
ap.add_argument("--centroid", help="Flag to use centroiding algorithm. Default True",
                action="store_false")
ap.add_argument("--ra", help="Right ascension", type=str, nargs="?", required=True)
ap.add_argument("--dec", help="Declination", type=str, nargs="?", required=True)
ap.add_argument("--posErr", help="Positional uncertainty for the centroiding algorithm in arcminutes. Default 0.5 arcminutes",
                type=float, nargs="?", default=0.5)
ap.add_argument("-o", "--outdir", nargs='?', help="Output dir name", type=str, default="data")
args = ap.parse_args()

ra = args.ra
dec = args.dec
outdir = args.outdir

ra, dec = convert_ra_dec(ra, dec)

name = get_source_names(ra, dec)[0]

outdir = create_outdir(outdir, name)

if not os.path.isdir(outdir):
    os.mkdir(outdir)

# TODO: do config file!
print("Using a positional uncertainty of %.2f arcminutes" % args.posErr)
myReq = ux.XRTProductRequest('a.gurpide-lasheras@soton.ac.uk', silent=False)
myReq.setGlobalPars(centroid=args.centroid, useSXPS=True, RA=ra, Dec=dec, getTargs=True, getT0=True,
                    name=name, posErr=args.posErr)
myReq.addLightCurve(binMeth='snapshot', allowUL="no")
myReq.addImage()

ok = myReq.submit()
print("Submitted?")
print(ok)
if not ok:
    print(myReq.submitError)
    sys.exit()

done = myReq.complete
start_time = time.time()
cumulative_time = 0
while not done:
  time.sleep(120)
  done = myReq.complete
  end_time = time.time()
  cumulative_time += cumulative_time + end_time - start_time
  print("Request completed? %r \n %.2f s running..." % (done,cumulative_time), end="")

myReq.downloadProducts('%s' % outdir, what=('LightCurve', "Image"), format='zip', clobber=True)
