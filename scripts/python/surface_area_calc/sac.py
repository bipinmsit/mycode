import scipy
import numpy as np
import matplotlib.pyplot as plt
import sklearn 
import math
from PIL import Image
from scipy.misc import imread, imshow, imsave

dx = imread('./dx_test2.tif')
dy = imread('./dy_test2.tif')
dem = imread('./DEM_test2.tif') 
demValid = dem > -32000.0
#Not required
#print(dem.shape)
#print(dx.shape)
#print(dy.shape)
surfArea = np.ones(dx.shape) * -32000.0
pixArea = 0.00325 ** 2 #Pixel Area in metre square
print("Processing Start.")
for r in range(0,dx.shape[0]):
	for c in range(0,dx.shape[1]):
		if(not math.isnan(dx[r][c])):
			surfArea[r][c] = (dx[r][c] **2 + dy[r][c]**2 + 1) ** 0.5;
surfArea = surfArea * pixArea 
im = Image.fromarray(surfArea)

im.save('./M1_Area5_act2.tif')
imsave('./M1_Area5_err2.tif',surfArea)

