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
import warnings
import pyLCR

ap = argparse.ArgumentParser(description='Fetch data from the Fermi-LAT lightcurve repository (https://fermi.gsfc.nasa.gov/ssc/data/access/lat/LightCurveRepository/index.html)')
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
names = result_table["MAIN_ID"]
name = names[0]
print(" Source name\n ------- \n %s" % name)
outdir += "/%s" % name

if not os.path.isdir(outdir):
    os.mkdir(outdir)
# https://indico.cern.ch/event/66737/contributions/2063638/attachments/1018688/1449988/MAPS_razzano.pdf slide 22
MJDREFI = 51910
MJDREFF = 7.42870370370370 * 10**-4
# get all identifiers, we need the 4FGL
result_table = Simbad.query_objectids(names[0])
# Assuming you have the result_table as shown in your question
for row in result_table["ID"]:
    if '4FGL' in row:
        fgl_idenitfier = row
        break  # Break out of the loop once you find the desired name
if fgl_idenitfier is None:
    warning.warn("Source %s not found in the Fermi catalog!" % name)
else:

    data = pyLCR.getLightCurve(fgl_idenitfier, cadence='daily', flux_type='photon', index_type='free', ts_min=4)
    print(data.get_info())

    plt.figure()
    plt.errorbar(data.met_detections  / 3600 / 24 + MJDREFF + MJDREFI, data.flux, yerr=[data.flux_error.T[0], data.flux_error.T[1]], ls="None")
    #plt.errorbar(data.met_upperlimits  / 3600 / 24 + MJDREFF + MJDREFI, data.flux_upper_limits, uplims=True)
    plt.xlabel("MJD (day)")
    plt.ylabel("Photon Flux [0.1 $-$ 100 GeV] (photons cm$^{-2} s^{-1}$) )")
    plt.savefig("%s/fermi_lat.png" % outdir)

    upp_lims = data.ts < data.ts_min
    outputs = np.array([data.met_detections / 3600 / 24 + MJDREFF + MJDREFI, data.flux, data.flux_error.T[0], data.flux_error.T[1], data.ts[~upp_lims],
                        data.photon_index,
                        data.photon_index_interval, data.fit_convergence[~upp_lims]])
    header = "#MJD\tflux\tflux_err_neg\tflux_err_pos\tts\tphoton_index\tphoton_index_err\tfit_convergence"

    outputfile = "fermi_lat.dat"
    np.savetxt(outputfile, outputs.T,
               delimiter="\t", fmt="%.6f", header=header)
    # save upper limits

    outputs = np.array([data.met_upperlimits  / 3600 / 24 + MJDREFF + MJDREFI, data.flux_upper_limits, data.ts[upp_lims], data.fit_convergence[upp_lims]])
    outputfile = "fermi_lat_upplims.dat"
    header = "#MJD\tflux\tts\tphoton_index\tphoton_index_err\tfit_convergence"
    np.savetxt(outputfile, outputs.T,
               delimiter="\t", fmt="%.6f", header=header)
