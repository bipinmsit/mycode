#!/usr/bin/env python

import pandas as pd
import os.path as path
import sys
import raster_processing.raster_translate as rt
import numpy as np
from numpy.linalg import norm
from subprocess import call

def help():
    print("Usage:- angle_from_coordinates.py <input-csv> <row-id-1> <row-id-2> \n")

def main(argv=None):
    if argv is None:
        argv = sys.argv

    
    data = argv[-3:]
    
    if (argv.count('-h') > 0) or (argv.count('--help')) > 0:
        help()
        return -1

    if len(argv) < 4:
        #When there are not enough arguments to use the command
        print("Use '-h' to view help",file=sys.stdout)
        print("ERROR 1. Not enough arguments",file=sys.stderr)
        return 1
        
    
    CSV_FILE = data[0]
    site_name_1 = data[1]
    site_name_2 = data[2]


    
    site_data = pd.read_csv(CSV_FILE)
    try:
        site_idx_1 = list(site_data[['site_name']].values).index(site_name_1)
        site_idx_2 = list(site_data[['site_name']].values).index(site_name_2)
    except Exception:
        print("Site not found!")
        sys.exit()

    p1_local = np.array(site_data[['ref_local_x', 'ref_local_y']].values[site_idx_1],
                        dtype=np.float)
    print("Local Coordinates 1 {}".format(p1_local))
    
    p1_global = np.array(site_data[['ref_global_x', 'ref_global_y']].values[site_idx_1],
                         dtype=np.float)
    print("Global Coordinates 1 {}".format(p1_global))

    p2_local = np.array(site_data[['ref_local_x', 'ref_local_y']].values[site_idx_2],
                        dtype=np.float)
    print("Local Coordinates 2 {}".format(p2_local))
    
    p2_global = np.array(site_data[['ref_global_x', 'ref_global_y']].values[site_idx_2],
                         dtype=np.float)
    print("Global Coordinates 2 {}".format(p2_global))
    
    dot_prod = np.dot(p1_local - p2_local, p1_global-p2_global)

    angle = np.arccos(dot_prod/(np.linalg.norm(p1_global - p2_global) * np.linalg.norm(p1_local - p2_local)))
    print("Angle of Rotation is {}".format(angle))
    
if __name__ == "__main__":
    sys.exit(main(sys.argv))
