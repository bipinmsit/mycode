"""
Gridding Process - 
1. Create new raster which will serve as shape reference for the grid.
2. Create grid based on shape reference raster
3. Set resolution of new raster such that each pixel is say, 5m x 5m
4. Sample the Image in 5m x 5m blocks such that each pixel in the new image corresponds
to a 5m x 5m block in the source image

"""
from subprocess import call
from raster_processing.raster_chunks import GeoChunks as gc
import gdal
import numpy as np
import csv

def grid_to_csv(inputGRID,outputCSV="./out.csv"):
    grid = gc(inputGRID)
    f=open(outputCSV,mode='w')
    w = csv.writer(f)
    xmin = grid.geo_trans[0]
    ymin = grid.geo_trans[3]
    xres = grid.geo_trans[1]
    yres = grid.geo_trans[5]
    w.writerow(['Latitude/Northing','Latitude/Northing','Longitude/Easting',
                'Longitude/Easting','Volume'])
    w.writerow(['Xmin','Xmax','Ymin','Ymax'])
    grid_arr = grid.read()
    ndv_mask = np.where(grid_arr == grid.no_data_value)
    grid_arr[ndv_mask] = 0
    for x in range(grid.data_bands[0].XSize):
        for y in range(grid.data_bands[0].YSize):
            _xmin = min(xmin + x*xres,xmin + (x+1)*xres)
            _xmax = max(xmin + x*xres,xmin + (x+1)*xres)
            _ymin = min(ymin + y*yres,ymin + (y+1)*yres)
            _ymax = max(ymin + y*yres,ymin + (y+1)*yres)
            _vol = grid_arr[y,x]
            r=[str(_xmin),str(_xmax),str(_ymin),str(_ymax),str(_vol)]
            w.writerow(r)

    f.close()

def dem_vol_grid(inputDEM, outputGrid="./grid.tif", gridSize=5.0, outputCSV="./grid.csv",
                 gridShapeRef="./grid_shape_ref.tif"):
    """
    Function to convert a dem to a gridded file, for verifying volume accuracy.
    gridSize -> Size of each grid in corresponding projection units, 
                ex. 5m x 5m if the input DEM is in UTM
    """
    dem = gc(inputDEM)
    #Creating Grid Shape reference
    call(['gdalwarp','-tr',str(np.copysign(gridSize,dem.geo_trans[0])),
          str(np.copysign(gridSize,dem.geo_trans[5])),inputDEM,gridShapeRef])
    
    grid_shape_ref = gc(gridShapeRef)

    grid = gc.create_from(other=grid_shape_ref,filename=outputGrid)
    #Setting GeoTransform of output grid to required values
    chunk_size = int(np.ceil(gridSize/dem.geo_trans[1]))
    chnk = dem.break_chunks(chunkx=chunk_size,chunky=chunk_size)
    xsize = dem.chunk_2d.shape[1]
    ysize = dem.chunk_2d.shape[0]
    grid_arr = grid.read()
    for x in range(xsize):
        for y in range(ysize):
            dem_arr = None
            dem_arr = dem.read(chunk=dem.chunk_2d[y,x])
            ndv_mask = np.where(dem_arr == dem.no_data_value)
            dem_arr[ndv_mask] = 0
            vol = np.sum(dem_arr) * dem.geo_trans[1]**2
            grid_arr[y,x] = vol
    ndv_mask = np.where(grid_arr == 0.0 )
    grid_arr[ndv_mask] = grid.no_data_value
    grid.write(arr=grid_arr)
    grid.data_gtif.FlushCache()
    grid_to_csv(outputGrid,outputCSV)


