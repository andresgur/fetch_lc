import matplotlib.pyplot as plt
import argparse
import os
import numpy as np
from astroquery.simbad import Simbad
import warnings
import pyLCR
from fetch_lc import create_outdir, get_source_names
from coordinates import convert_ra_dec

delimiter = ","

ap = argparse.ArgumentParser(description='Fetch data from the Fermi-LAT lightcurve repository (https://fermi.gsfc.nasa.gov/ssc/data/access/lat/LightCurveRepository/index.html)')
ap.add_argument("--ra", help="Right ascension", type=str, nargs="?", required=True)
ap.add_argument("--dec", help="Declination", type=str, nargs="?", required=True)
ap.add_argument("-o", "--outdir", nargs='?', help="Output dir name", type=str, default="data")
args = ap.parse_args()

ra_str = args.ra
dec_str = args.dec
outdir = args.outdir

if not os.path.isdir(outdir):
    os.mkdir(outdir)

ra, dec = convert_ra_dec(ra_str, dec_str)
name = get_source_names(ra, dec)[0]

outdir = create_outdir(outdir, name)
# https://indico.cern.ch/event/66737/contributions/2063638/attachments/1018688/1449988/MAPS_razzano.pdf slide 22
MJDREFI = 51910
MJDREFF = 7.42870370370370 * 10**-4
# get all identifiers, we need the 4FGL
result_table = Simbad.query_objectids(name)
# Assuming you have the result_table as shown in your question
fgl_idenitfier = None
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
                        data.photon_index - data.photon_index_interval, data.fit_convergence[~upp_lims]])
    header = "MJD,flux,flux_err_neg,flux_err_pos,ts,photon_index,photon_index_err,fit_convergence"

    outputfile = "%s/fermi_lat.dat" % outdir

    np.savetxt(outputfile, outputs.T,
               delimiter=delimiter, fmt="%.6e", header=header)
    # save upper limits

    outputs = np.array([data.met_upperlimits  / 3600 / 24 + MJDREFF + MJDREFI, data.flux_upper_limits, data.ts[upp_lims], data.fit_convergence[upp_lims]])
    outputfile = "%s/fermi_lat_upplims.dat" % outdir
    header = "MJD,flux,ts,photon_index,photon_index_err,fit_convergence"
    np.savetxt(outputfile, outputs.T,
               delimiter=delimiter, fmt="%.6e", header=header)
