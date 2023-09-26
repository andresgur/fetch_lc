import matplotlib.pyplot as plt
import argparse
import os
import time
import numpy as np
import subprocess
from multiprocessing import Process
from astroquery.simbad import Simbad
from coordinates import convert_ra_dec


def get_source_names(ra, dec):
    result_table = Simbad.query_region("%.5f, %+.5f" % (ra, dec))
    name = result_table[0]["MAIN_ID"]
    print(" Source name\n --------- \n %s" % name)
    return result_table["MAIN_ID"]

def create_outdir(subdir, source_name):
    outdir =  subdir + "/" + source_name.replace(" ", "_")
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    return outdir


def fetch_data(archive, ra, dec, outdir):
    """Wrapper to run fetch data of each instrument in parallel"""
    command = f"python {archive}.py --ra '{ra}' --dec '{dec}' -o {outdir}"
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    print(out)

if __name__ == "__main__":

    ap = argparse.ArgumentParser(description='Fetch data from various archival data (so far TESS, PTF, ZTF, Swift-XRT, WISE)')
    ap.add_argument("--ra", help="Right ascension. Either space or ':' separated or decimal degrees", type=str, nargs="?", required=True)
    ap.add_argument("--dec", help="Declination. Either space or ':' separated or decimal degrees", type=str, nargs="?", required=True)
    ap.add_argument("-o", "--outdir", nargs='?', help="Output dir name", type=str, default="data")
    args = ap.parse_args()

    ra = args.ra
    dec = args.dec

    if not os.path.isdir(args.outdir):
        os.mkdir(args.outdir)

    ra, dec = convert_ra_dec(ra, dec)
    name = get_source_names(ra, dec)[0]
    outdir = create_outdir(args.outdir, name)

    archives = ["tess", "ptf", "ztf", "wise", "mast", "fermi", "swift"]
    processes = []
    for archive in archives:
        print("Getting data from %s" % archive)
        process = Process(target=fetch_data, args=(archive, ra, dec, args.outdir))
        processes.append(process)
        process.start()
        # Wait for all processes to finish
    for process in processes:
        process.join()

    os.chdir(outdir)
    p = subprocess.Popen("python ../../plot_data.py", stdout=subprocess.PIPE, shell=True)
    out,err = p.communicate()
    print(out)

    file = open("source.log", "w+")
    file.write(name)
    file.write("\nRA: %.5f, DEC: %.5f" % (ra, dec))
    file.close()

    print("Data stored to %s" % outdir)
