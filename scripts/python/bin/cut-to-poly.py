#!/usr/bin/env python
from subprocess import call
import sys
from raster_processing.raster_chunks import GeoChunks as  gc
def help():
    print("Usage:- cut-to-poly.py <options> <input-Gtiff> <input-mask-Polygon> <output-masked-DEM>\n"\
          "          <options> can include ->\n"\
          "           -ow,--overwrite           -> Force overwrite of output file, if it already exists  \n"\
          "           -h,--help                 -> print this help message\n"\
          "           --gdal_options '<options>'    -> use gdalwarp options in the command")
def main(argv=None):
    argv = sys.argv
    #Add functionality to sanity check commands passed through this
    
    options = argv[1:-3]
    data = argv[-3:]
    #Overwrite flag
    ow_flag = False
    if (argv.count('-h') > 0) or (argv.count('--help')) > 0:
        help()
        return -1

    if len(argv) < 4:
        #When there are not enough arguments to use the command
        print("Use '-h' to view help",file=sys.stdout)
        print("ERROR 1. Not enough arguments",file=sys.stderr)
        return 1
    if(options.count('-ow') > 0) or (options.count('--overwrite') > 0):
        ow_flag = True
    gdal_options = None
    if options.count('--gdal_options') > 0:
        g_idx = options.index('--gdal_options')
        gdal_options = options[g_idx + 1].split(' ')
        print(gdal_options)
    ref_dem = gc(data[0])
    base_geo_trans = ref_dem.geo_trans
    xsize = str(base_geo_trans[1])
    ysize = str(base_geo_trans[5])
    cmd = str("gdalwarp -of GTiff -cutline").split(' ') + [data[1]] + str("-crop_to_cutline -tr").split(' ') +\
            [xsize] + [ysize]
    if gdal_options is not None:
        cmd = cmd + gdal_options
    
    if ow_flag:
        cmd = cmd + ["-overwrite"]
    cmd = cmd + [data[0]] +  [data[2]]
    print(cmd)
    ret_code = call(cmd)
    print(ret_code)
    if ret_code is 0:
        print("Mask Operation Completed.\nOutput file present at " + data[2],file=sys.stdout)
    return ret_code
   

if __name__ == "__main__":
    sys.exit(main())