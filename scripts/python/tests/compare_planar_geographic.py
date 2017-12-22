import glob
import gdal
import numpy as np

from raster_processing.raster_chunks import GeoChunks as gc

def compare_pl_gr(file_pl, file_gr):
    dem_pl = gc(file_pl)
    dem_gr = gc(file_gr)

    arr_pl = dem_pl.read()
    arr_gr = dem_gr.read()

    mask_pl = np.where(arr_pl == dem_pl.no_data_value)
    mask_gr = np.where(arr_pl == dem_gr.no_data_value)

    arr_pl[mask_pl] = 0.0
    arr_gr[mask_gr] = 0.0

    if arr_pl.shape != arr_gr.shape:
        return False

    if dem_pl.geo_trans != dem_gr.geo_trans:
        return False
    
    diff_pl_gr = np.sum(np.abs(arr_pl - arr_gr))

    if diff_pl_gr != 0.0:
        return False

    return True

files_pl_dem = glob.glob("./*planer-DEM*")
files_gr_dem = glob.glob("./*geographic-DEM*")

files_pl_dem.sort()
files_gr_dem.sort()
print("Planar DEM files are: - \n" + str(files_pl_dem))
print("Geographic DEM files are: - \n" + str(files_gr_dem))

len_files = len(files_pl_dem)

if len_files != len(files_gr_dem):
    raise ValueError("Number of planar DEMs is not equal to number of geographic DEMs")

for i in range(len_files):
    comp_result = compare_pl_gr(files_pl_dem[i], files_gr_dem[i])
    if comp_result is False:
        print("Comparison Failed. Planar and Geographic DEMs are not the same")
        raise ValueError(files_pl_dem[i] + " != " + files_gr_dem[i])

print("All Geographic and Planar DEMs are the same, pixel for pixel")


