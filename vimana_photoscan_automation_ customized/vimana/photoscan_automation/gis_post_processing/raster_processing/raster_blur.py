from raster_chunks import GeoChunks as GC
import cv2
import numpy as np



def box_blur(in_file, out_file, filter_size=51, b_idx=0):
    """
    Function to Filter the image with a box filter of specified dimension
    
    """
    src = GC(in_file)
    print(src.no_data_value)
    #Insert assertation to ensure that b_idx < src.nbands
    dest = GC.create_from(src, out_file)
    for ch in src.break_chunks(paddingX=2*filter_size, paddingY=2*filter_size):
        src_chunk = src.read(chunk=ch)
        #Processing
        src_chunk[np.where(src_chunk == src.no_data_value)] = 0
        dest_chunk = cv2.blur(src_chunk, (filter_size, filter_size) )
        dest_chunk[np.where(src_chunk == src.no_data_value)] = dest.no_data_value
        
        #Write to new DEM
        dest.write(dest_chunk, chunk=ch)
    
    dest=None
    return True