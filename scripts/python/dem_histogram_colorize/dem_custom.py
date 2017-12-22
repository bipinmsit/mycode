import gdal
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate as itp
from PIL import Image 


def plot_hist(tif_loc,out_hist_loc,b_no=255):
	#Shows histogram of DEM values, with data split into 'b_no=255' bins. 255 is default value, and
	# can be increased for better histogram resolution
    gTIF = gdal.Open(tif_loc)
    dem_band = gTIF.GetRasterBand(1)
	dem_ndv = dem_band.GetNoDataValue()
    dem_2d = dem_band.ReadAsArray()
    dem_flat = dem_2d.flatten()
    dem_clean = np.delete(dem_flat, np.where(dem_flat == dem_ndv ))
    #checking if remaining values are good
    print('Min Value is ' + str(min(dem_clean)))
    print('Max Value is ' + str(max(dem_clean)))

    plt.hist(dem_clean,b_no)
    plt.savefig(out_hist_loc)

def color_dem(in_tif_loc,out_tif_loc,d_bands,col_bands):
	"""
	Given input DEM, colorize it acc to depth value bands, and color bands mentioned by user
	Note that smallest value in d_bands must atleast be slightly smaller than the smallest value in DEM, 
	Besides the NoDataValue. Similarly, the highest value must be a little higher. 
	
	Expected format is taken from color files used in gdaldem's color relief method so, 
	 0   0   0   0
	 100 255 255 255
	would map a depth of 0 to black, and a depth of 100 to the brightest white. 
	this would be passed to function as d_bands = [0 255], col_bands = [[0,0,0],[255,255,255]]
	d_bands[d_bands.index(min(d_bands))] = 	d_bands[d_bands.index(min(d_bands))] - 1
	d_bands[d_bands.index(max(d_bands))] = 	d_bands[d_bands.index(min(d_bands))] + 1
	"""
	#Setting up interpolators
	c_bands = np.array(col_bands)
	r_itp = itp.interp1d(d_bands,c_bands[:,0])
	g_itp = itp.interp1d(d_bands,c_bands[:,1])
	b_itp = itp.interp1d(d_bands,c_bands[:,2])

	gTIF = gdal.Open(in_tif_loc)
	dem_band = gTIF.GetRasterBand(1)
	dem_ndv = dem_band.GetNoDataValue()
	dem_2d = dem_band.ReadAsArray()
	color_dem = np.zeros([dem_2d.shape[0],dem_2d.shape[1],3],dtype=np.uint8)
	for r in range(dem_2d.shape[0]):
		for c in range(dem_2d.shape[1]):
			if dem_2d[r,c] != dem_ndv:
				color_dem[r,c,0] = int(r_itp(dem_2d[r,c]))
				color_dem[r,c,1] = int(g_itp(dem_2d[r,c]))
				color_dem[r,c,2] = int(b_itp(dem_2d[r,c]))
	
	img = Image.fromarray(color_dem)
	img.save(out_tif_loc)
    		
    
	

