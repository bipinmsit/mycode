from raster_processing.raster_chunks import GeoChunks as gc
import numpy as np
from subprocess import call
import matplotlib.pyplot as plt
import gdal
import sys


def match_shape_DEM(referenceDEM,terrainDEM,tempDEM="./temp_1234.tif"):
    """
    Ensures that shape of reference DEM and the new terrain DEM are the same.
    This is done by:
    1. Ensuring that the GSD/Resolution/PixelSize match, in both
    2. Ensure that the extent of both images are the size
    """
    ref_dem = gc(referenceDEM)
    new_dem = gc(terrainDEM)
    try:
        assert(ref_dem.data_bands[0].XSize == new_dem.data_bands[0].XSize)
        assert(ref_dem.data_bands[0].YSize == new_dem.data_bands[0].YSize)
    except:
        """
        Assumptions:-
        1. TerrainDEM already has the same projection system as the original DEM
        
        To-Do:-
        1. Get extent of reference Image
        2. Get projection of reference Image (..required?)
        3. Use extent, projection, and pixel size of original image with GDAl to
           force creation of new file with same size as reference DEM
        """
        #Geographic Extents in X direction
        x_min = str(ref_dem.geo_extent_x[0])
        x_max = str(ref_dem.geo_extent_x[1])
        #Geographic Extents in Y direction
        y_min = str(ref_dem.geo_extent_y[0])
        y_max = str(ref_dem.geo_extent_y[1])
        #Pixel Resolution along both axes
        x_size = str(ref_dem.geo_trans[1])
        y_size = str(ref_dem.geo_trans[5])
        ref_dem = None
        new_dem = None
        #Code to change size of terrainDEM to size of reference DEM
        call(["gdalwarp", "-te", x_min, y_min, x_max, y_max, "-tr",
              x_size, y_size, "-overwrite", terrainDEM, tempDEM])
        call(["mv", tempDEM, terrainDEM])
        pass
        
    pass




def create_delta_DEM(referenceDEM, terrainDEM, deltaDEM="./delta.tif"):
    """
    For each co-ordinate in referenceDEM and terrainDEM,
    create a grid where value of each co-ordinate is
    
    delta[x, y] = referenceDEM[x, y] - terrainDEM[x, y]
    referenceDEM = "/path/to/referenceDEM/dem"
    terrainDEM = "/path/to/interpolated/dem"
    """
    ref_dem = gc(referenceDEM)
    new_dem = gc(terrainDEM)
    delta_dem = gc.create_from(ref_dem, deltaDEM)
    #Ensuring that the size of the two rasters are the same
    try:
        assert(ref_dem.data_bands[0].XSize == new_dem.data_bands[0].XSize)
        assert(ref_dem.data_bands[0].YSize == new_dem.data_bands[0].YSize)
    except:
        print('Error. Size of input DEMs do not match.',file=sys.stderr)
        return 2
    if ref_dem.data_bands[0].XSize > gc.x_chunk_size:
        for ch in ref_dem.break_chunks():
            ref_arr = ref_dem.read(chunk=ch)
            ref_mask = np.where(ref_arr == ref_dem.no_data_value)
            ref_arr[ref_mask] = 0
            new_arr = new_dem.read(chunk=ch)
            new_arr[ref_mask] = 0
            delta_arr = ref_arr - new_arr
            delta_dem.write(delta_arr,chunk=ch)
    else:
        ref_arr = ref_dem.read()
        ref_mask = np.where(ref_arr == ref_dem.no_data_value)
        ref_arr[ref_mask] = 0
        new_arr = new_dem.read()
        new_arr[ref_mask] = 0
        delta_arr = ref_arr - new_arr
        delta_dem.write(delta_arr)
    delta_dem = None
    return 0
    pass

def apply_mask_poly(baseDEM, maskPoly,maskDEM):
    """
    Apply mask to base to get maskDEM as output.
    Values that are masked out will be set to No data value of the baseDEM.
    """
    ref_dem = gc(baseDEM)
    
    base_geo_trans = ref_dem.geo_trans
    #Geographic Extents in X direction
    x_min = str(ref_dem.geo_extent_x[0])
    x_max = str(ref_dem.geo_extent_x[1])
    #Geographic Extents in Y direction
    y_min = str(ref_dem.geo_extent_y[0])
    y_max = str(ref_dem.geo_extent_y[1])

    xsize = str(base_geo_trans[1])
    ysize = str(base_geo_trans[5])
    call(["gdalwarp", "-ot", "Float32", "-of", "GTiff", "-cutline", maskPoly,
          "-te", x_min, y_min, x_max, y_max,"-overwrite","-crop_to_cutline",
          "-tr", xsize, ysize, baseDEM, maskDEM])
    print("Mask Operation Completed.\nOutput file present at " + maskDEM)
    pass

def DEM_histogram(histDEM, default=False, hist_min = -50, hist_max = 50, hist_nbins=1000):
    """
    gives me a dictionary of value, freq pairs
    for each distinct value in the deltaDEM which
    is not removedValue
    """
    hist_gtif = gc(histDEM)
    if default is False:
        hist_tuple = hist_gtif.data_bands[0].GetHistogram(buckets=hist_nbins,min=hist_min,max=hist_max)
        hist_arr = np.array(hist_tuple)
        hist_keys = np.linspace(hist_min, hist_max, hist_nbins)
        hist_dict = dict(zip(hist_keys, hist_arr))
        plt.bar(hist_keys, hist_arr, align='center')
        plt.show()
        return hist_dict
        
    else:    
        hist_tuple = hist_gtif.data_bands[0].GetDefaultHistogram()
        hist_min = hist_tuple[0]
        hist_max = hist_tuple[1]
        hist_nbins = hist_tuple[2]
        hist_arr = np.array(hist_tuple[3])
        hist_keys = np.linspace(hist_min, hist_max, hist_nbins)
        hist_dict = dict(zip(hist_keys, hist_arr))
        plt.bar(hist_keys, hist_arr, align='center')
        plt.show()
        return hist_dict
        

def performance(hist, minVal, meanTreeHeight, k, maxVal):
    """
    True/False indicating whether hist is within bounds
    """
    if min(hist.keys()) < minVal:
        return False
    if max(hist.keys()) > maxVal:
        return False
    


    pass
    
    """
    variance calc
    
    In [46]: for ch in chnks:
    ...:     arr = []
    ...:     for dem in dem_arr:
    ...:         d_arr = dem.read(chunk=ch)
    ...:         d_arr[np.where(d_arr == dem.no_data_value)] = 0
    ...:         arr.append(d_arr)
    ...:     stacked = np.dstack(tuple(arr))
    ...:     var_arr = np.var(stacked,axis=2)
    ...:     var_arr[np.where(var_arr == 0)] = var_out.no_data_value
    ...:     var_out.write(var_arr,chunk=ch)
    ...:     

    """