#!/usr/bin/env python
from subprocess import call
import sys
from raster_processing.raster_chunks import GeoChunks as  gc
import dem_processing.dem_perf_check as dpc
def help():
    print("Usage:- delta-dem.py <options> <input-reference-DEM> <input-test-DEM> <output-delta-DEM>\n"\
          "          <options> can include ->\n"\
          "           -ow,--overwrite   -> Force overwrite of output file, if it already exists  \n"\
          "           -h,--help         ->  print this help message\n")
def main(argv=None):
    argv = sys.argv
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

    ref_dem = gc(data[0])
    new_dem = gc(data[1])
    
    #Ensuring that the size of the two rasters are the same
    try:
        assert(ref_dem.data_bands[0].XSize == new_dem.data_bands[0].XSize)
        assert(ref_dem.data_bands[0].YSize == new_dem.data_bands[0].YSize)
    except:
        print('Error. Size of input DEMs do not match.\n'\
              "Match size with size-match-dem.py before proceeding",file=sys.stdout)
        print('Error. Size of input DEMs do not match.',file=sys.stderr)
        return 2
    return_code = dpc.create_delta_DEM(referenceDEM=data[0],terrainDEM=data[1],deltaDEM=data[2])
    print("Delta DEM calculation completed.\nOutput file present at " + data[2],file=sys.stdout)
    return return_code


if __name__ == "__main__":
    sys.exit(main())