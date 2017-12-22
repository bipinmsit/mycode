#!/usr/bin/env python
import sys
import vector_processing.point_processing as pp
def help():
    print("volume-from-shape.py <options> <input_dem> <shape_file>\n" \
          "Options can include :- \n "\
          "         -b <base-dem> : To specify from which DEM the height values will be sampled from "\
          "         -h            : To print this help message")
def main(argv=None):
    argv = sys.argv
    options = argv[1:-2]
	data = argv[-2:]
    if options.count('-b') > 0:
        b_idx = options.index('-b')
        base_dem = options[b_idx + 1]
        

