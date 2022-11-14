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
from astroquery.utils.tap.core import TapPlus
from astroquery.gaia import Gaia
from coordinates import convert_ra_dec

# https://www.ptf.caltech.edu/page/lcgui
ap = argparse.ArgumentParser(description='Fetch data from ZTF https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html')
ap.add_argument("--ra", help="Right ascension", type=float, nargs="?", required=True)
ap.add_argument("--dec", help="Declination", type=float, nargs="?", required=True)
ap.add_argument("-o", "--outdir", nargs='?', help="Output dir name", type=str, default="data")
args = ap.parse_args()

ra = args.ra
dec = args.dec
outdir = args.outdir

ra, dec = convert_ra_dec(ra, dec)

#user='agurpi01', password='@1EUROjakob@'
Gaia.login(user='agurpi01', password='@1EUROjakob@')

gaia = TapPlus(url="http://gea.esac.esa.int/tap-server/tap")
tables = gaia.load_tables(only_names=True)
for table in (tables):
    print(table.get_qualified_name())
