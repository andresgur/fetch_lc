import matplotlib.pyplot as plt
from swift_lc import SwiftLightcurve
import readingutils as ru
import os
import warnings
import astropy.units as u
import numpy as np
import argparse
import glob
import warnings
from matplotlib.pyplot import cm

style_file = '/home/andresgur/.config/matplotlib/stylelib/paper.mplstyle'
if os.path.isfile(style_file):
    plt.style.use(style_file)
else:
    warnings.warn("Style file not found!")

ap = argparse.ArgumentParser(description='Plot lightcurves from the different observatories')
ap.add_argument('--tmin', nargs="?", help="Minimum MJD to plot", type=float, default=0)
ap.add_argument('--tmax', nargs="?", help="Maximum MJD to plot. Default Max value in the data", type=float, default=-1)
args = ap.parse_args()

current_dir = os.getcwd()

# get source name
source_name = os.path.basename(os.getcwd())

labels = ["Swift-XRT (ct/s)", "ZTF/PTF (mag)", "TESS (mag)", "Wise (mag)"]

# "Swift-XRT (ct/s)",
fig, axes = plt.subplots(len(labels),1 ,sharex=True, gridspec_kw={"hspace":0.1, "wspace":0}, figsize=(24, 12))
for ax, lab in zip(axes, labels):
    ax.set_ylabel(lab)
axes[-1].set_xlabel("MJD")
fig.suptitle(source_name, fontsize=22, y=0.92)

# SWIFT
glob_list = glob.glob("./USER*/lc")

if len(glob_list) > 1:
    swift_dir = glob_list[0]
    os.chdir(swift_dir)

    f = open("t0.date")
    lines = f.readlines()
    f.close()
    start_date = lines[1].split("at")[0]
    swift_zero_point = ru.read_zero_point()

    swift_data = SwiftLightcurve(upper_limit_file=None, start_date=start_date)
    axes[0].errorbar(swift_data.timestamps.to(u.d).value + swift_zero_point.mjd, swift_data.rate.value,
                     yerr=swift_data.errors.value, label="PC mode", ls="None", color="black", fmt=".") # , fmt="+"
    swift_data = SwiftLightcurve("WTCURVE.qdp", upper_limit_file=None, start_date=start_date)

    os.chdir(current_dir)
    axes[0].errorbar(swift_data.timestamps.to(u.d).value + swift_zero_point.mjd, swift_data.rate.value,
                     yerr=swift_data.errors.value, label="WT mode", ls="None", color="blue", fmt=".") # , fmt="+"
    axes[0].legend()
else:
    warnings.warn("SWIFT directory not found!")


#ax2.legend()
bands = ["i", "g", "r"]
for band in bands:
    ztf_band = np.genfromtxt("ztf_z%s.dat" % band, names=True)
    axes[1].errorbar(ztf_band['t'], ztf_band['mag'], yerr=ztf_band['err'], ls='None', label="ZTF%s" % band) # , fmt="+"

bands = ["g", "R"]
colors = iter(cm.tab20(np.linspace(0.1, 0.9, len(bands))))
for band, c in zip(bands, colors):
    data_files = glob.glob("ptf_%s_*.dat" % band) # get all files from all sources as they may have different identifiers
    for data_file in data_files:
        ptf_band = np.genfromtxt(data_file, names=True)
        axes[1].errorbar(ptf_band['t'], ptf_band['mag'], yerr=ptf_band['err'],
                         ls='None', label="PTF%s" % band, color=c) # , fmt="+"
# remove repeating legends
handles, labels = axes[1].get_legend_handles_labels()
by_label = dict(zip(labels, handles))
axes[1].legend(by_label.values(), by_label.keys())
#axes[1].legend()

bands = ["w1", "w2", "w3", "w4"]
for band in bands:
    data_file = "wise_%s.dat" % band
    if os.path.isfile(data_file):
        wise_band = np.genfromtxt(data_file, names=True, delimiter=",")
        axes[-1].errorbar(wise_band['mjd'], wise_band['%smpro_ep' % band], yerr=wise_band['%ssigmpro_ep' % band],
                         ls='None', label="%s" % band) # , fmt="+"
    else:
        warnings.warn("WISE %s file not found!" % data_file)
    axes[-1].legend()
# TESS
bands = ["TESS", "K2", "KEPLER"]
for band in bands:
    files = glob.glob("%s_*.dat" % band)
    for data_file in files:
        tess_band = np.genfromtxt(data_file, names=True, delimiter="\t")
        axes[2].errorbar(tess_band['t_day'], tess_band["mag_err"], yerr=tess_band["err"],
                         ls='None', label="%s" % band) # , fmt="+"
axes[2].legend()

if args.tmin!=0:
    tmin = args.tmin
    for ax in axes:
        ax.set_xlim(left=tmin)
if args.tmax !=-1:
    tmax = args.tmax
    for ax in axes:
        ax.set_xlim(right=tmax)
plt.savefig("dataset.png", bbox_inches="tight")
