import gdal
import cv2
import numpy as np
from raster_processing.raster_chunks import GeoChunks as gc

#GIPPY does not work with padding. Create your own module to access raster bands in chunks lke gippy does.
def gaussian_blur(in_file, out_file, std_dev=10.0, b_idx=0):
    """
    Function to Filter the image with a Gaussian filter 
    of specified standard deviation
    
    """
    src = gc(in_file)
    #Insert assertation to ensure that b_idx < src.n_bands
    assert b_idx < src.n_bands
    dest = gc.create_from(src, out_file)
    
    #Calculating filter_size from standard deviation of Gaussian Kernel
    filter_size = int(5 * std_dev)
    # Ensuring filtersize is odd
    filter_size = filter_size + (filter_size + 1) % 2

    for ch in src.break_chunks(padding_x=2*filter_size, padding_y=2*filter_size):
        src_chunk = src.read(chunk=ch)
        #Processing
        src_ndv_mask = np.where(src_chunk == src.no_data_value) 
        src_chunk[src_ndv_mask] = 0
        dest_chunk = cv2.GaussianBlur(src_chunk, (filter_size, filter_size),std_dev)
        dest_chunk[src_ndv_mask] = dest.no_data_value
        #Write to new DEM
        dest.write(dest_chunk, chunk=ch)
    
    dest=None
    return True


def box_blur(in_file, out_file, filter_size=51, b_idx=0):
    """
    Function to Filter the image with a box filter of specified dimension
    
    """
    src = gc(in_file)
    print(src.no_data_value)
    #Insert assertation to ensure that b_idx < src.n_bands
    dest = gc.create_from(src, out_file)
    for ch in src.break_chunks(padding_x=2*filter_size, padding_y=2*filter_size):
        src_chunk = src.read(chunk=ch)
        #Processing
        src_chunk[np.where(src_chunk == src.no_data_value)] = 0
        dest_chunk = cv2.blur(src_chunk, (filter_size, filter_size) )
        dest_chunk[np.where(src_chunk == src.no_data_value)] = dest.no_data_value
        
        #Write to new DEM
        dest.write(dest_chunk, chunk=ch)
    
    dest=None
    return True


def maskDEM(dem_input, mask_input, file_output, val_threshold):
    # Mask DEM values if corresponding location in mask has values greater than the (val_)threshold
    # mask input corresponds to slope file, in our use case
    dem_Tif = gc(dem_input)
    dem_ndv = dem_Tif.no_data_value

    # Preparing mask
    mask_Tif = gc(mask_input)
    output_DEM = gc.create_from(dem_Tif, file_output)

    for ch in dem_Tif.break_chunks():
        dem_arr = dem_Tif.read(chunk=ch)
        mask_arr = mask_Tif.read(chunk=ch)
        dem_mask = np.where(mask_arr > val_threshold)
        dem_arr[dem_mask] = dem_ndv
        output_DEM.write(dem_arr, chunk=ch)

    output_DEM = None
    return True
    # Note that final image's CRS will match source image.

def sumDEM(dem_input):
    gtif = gc(dem_input)
    vol_sum = 0.0
    for ch in gtif.break_chunks():
        arr = gtif.read(chunk=ch)
        arr[np.where(np.isnan(arr))] = 0.0
        arr [np.where(arr == gtif.no_data_value)] = 0.0
        t_sum = np.sum(arr)
        vol_sum = vol_sum + t_sum
    return vol_sum

def sumPixDEM(dem_input):
    gtif = gc(dem_input)
    vol_sum = 0.0
    for ch in gtif.break_chunks():
        arr = gtif.read(chunk=ch)
        if(np.isnan(gtif.no_data_value)):
            arr [np.where(np.isnan(arr))] = -9999
            arr [np.where(arr != -9999)] = 1
            arr [np.where(arr == -9999)] = 0
        else:
            arr [np.where(arr != gtif.no_data_value)] = 1
            arr [np.where(arr == gtif.no_data_value)] = 0
        t_sum = np.sum(arr)
        vol_sum = vol_sum + t_sum
    return vol_sum

def volumeRefDEM(referenceDEM,otherDEM):
    refDEM = gc(referenceDEM)
    othDEM = gc(otherDEM)
    try:
        #Ensuring Size and resolution match in the X direction
        assert refDEM.geo_extent_x == othDEM.geo_extent_x and refDEM.geo_trans[1] == othDEM.geo_trans[1]
        #Ensuring Size and resolution match in the Y direction
        assert refDEM.geo_extent_y == othDEM.geo_extent_y and refDEM.geo_trans[-1] == othDEM.geo_trans[-1]
    except:
        print("Sizes of the Two DEMs do not match. Match shape of the two DEMs before proceeding.")
        return False
    vol_sum = 0.0 
    for ch in refDEM.break_chunks():
        refArr = refDEM.read(chunk=ch)
        othArr = othDEM.read(chunk=ch)
        refMask = np.where(refArr == refDEM.no_data_value)
        refArr[np.where(np.isnan(refArr))] = 0
        refArr[refMask] = 0
        othArr[refMask] = 0
        deltaArr = refArr - othArr
        t_sum = np.sum(deltaArr)
        vol_sum = vol_sum + t_sum
    return vol_sum * refDEM.geo_trans[1] ** 2

def volumeRefPlane(referenceDEM, planeheight=None):
    refDEM = gc(referenceDEM)
    if planeheight is None:
        return sumDEM(referenceDEM) * refDEM.geo_trans[1] ** 2
    else:
        vol_sum = np.long(0.0)
        for ch in refDEM.break_chunks():
            refArr = None
            refArr = refDEM.read(chunk=ch)
            refArr[np.where(np.isnan(refArr))] = 0.0
            mask = np.where(refArr == refDEM.no_data_value)
            refArr[mask] = 0.0
            ref2 = planeheight - refArr
            ref2[mask] = 0.0
            t_sum = np.sum(ref2)
            vol_sum = vol_sum + t_sum
        return vol_sum * refDEM.geo_trans[1] ** 2
