#!/usr/bin/env python

import pandas as pd
import os.path as path
import sys
import raster_processing.raster_translate as rt
import numpy as np
from numpy.linalg import norm
from subprocess import call

def help():
    print("Usage:- local2global.py <options> <input-csv> <input-raster> \n"\
          "          <options> can include ->\n"\
          "           -co, --compress        -> Compress Output file"
          "           -ow, --overwrite       -> Apply transformation on existing file"
          "           --name <name>          -> mention name of site\n"
          "           -h,--help              -> print this help message\n")

def main(argv=None):
    if argv is None:
        argv = sys.argv

    options = argv[1:-2]
    data = argv[-2:]
    site_name = None
    ow_flag = False
    compress_flag = False
    if options.count('-ow') > 0 or options.count('--overwrite') > 0:
        ow_flag = True
    if options.count('-co') > 0 or options.count('--compress') > 0:
        compress_flag = True

    if (argv.count('-h') > 0) or (argv.count('--help')) > 0:
        help()
        return -1

    if len(argv) < 3:
        #When there are not enough arguments to use the command
        print("Use '-h' to view help",file=sys.stdout)
        print("ERROR 1. Not enough arguments",file=sys.stderr)
        return 1
    
    if options.count('--name') > 0:
        n_idx = options.index('--name')
        site_name = options[n_idx + 1]
        print(site_name)
    
    site_srs  = None
    if options.count('--srs') > 0:
        srs_idx = options.index('--srs')
        site_srs = options[srs_idx + 1]
        print("Site SRS: {}".format(site_srs))
    
    CSV_FILE = data[0]
    IN_RASTER = path.realpath(data[1])
    RASTER = path.join(path.dirname(IN_RASTER), 'input_raster.tif')
    OUT_RASTER = IN_RASTER.replace('.tif', '_global.tif')
    call(['cp',IN_RASTER, RASTER])


    
    site_data = pd.read_csv(CSV_FILE)
    if site_name is None:
        site_idx = 0
        print("Using default site!")
    else:
        try:
            site_idx = list(site_data[['site_name']].values).index(site_name)
        except Exception:
            site_idx = 0
            print("Site not found!")
            sys.exit()
    
    p1_local = np.array(site_data[['ref_local_x', 'ref_local_y']].values[site_idx],
                        dtype=np.float)
    print("Local Coordinates are {}".format(p1_local))
    
    p1_global = np.array(site_data[['ref_global_x', 'ref_global_y']].values[site_idx],
                         dtype=np.float)
    print("Global Coordinates are {}".format(p1_global))

    angle = site_data[['rotate_angle_deg']].values[site_idx]
    print("Angle of Rotation is {}".format(angle))
    delta = p1_global - p1_local
    rt.translate(RASTER, delta)
    rt.rotate(RASTER, angle_deg=angle, centre_rotation=p1_global)
    gdal_base = ['gdalwarp', '-overwrite']

    if compress_flag:
        gdal_base.append('-co')
        gdal_base.append('COMPRESS=JPEG')
    
    if site_srs:
        gdal_base.append('-t_srs')
        gdal_base.append(site_srs)
        #TODO: Remove below lines!
        gdal_base.append('-s_srs')
        gdal_base.append(site_srs)
        
    # Input Raster
    gdal_base.append(RASTER)
    # Output Raster
    gdal_base.append(OUT_RASTER)
    # making function call
    call(gdal_base)
    if ow_flag:
        call(['mv', OUT_RASTER, RASTER])
        temp_raster = RASTER
    print("\n\nOutput file present at {}".format(OUT_RASTER))
if __name__ == "__main__":
    sys.exit(main(sys.argv))
