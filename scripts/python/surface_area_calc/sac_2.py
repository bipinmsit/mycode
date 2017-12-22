import scipy
import numpy as np
import matplotlib.pyplot as plt
import sklearn
from scipy.misc import imread, imsave, imshow
import math
from PIL import Image

dem = imread('./DEM_test2.tif')
#dem = np.random.random((100, 100)) * 800

demValid = dem > -32000.0
L = np.float64(0.00325) # Pix Dimension
L2 = L * (2 ** 0.5)
L_arr = np.array([L2,L])
hcShape = tuple([dem.shape[0],dem.shape[1],8])
surfAreaDiv = np.zeros(hcShape)
surfArea = np.ones(dem.shape) * -32000.0
hypCalc = np.zeros(hcShape)
ordArray = [0,1,2,4,7,6,5,3]
print("File opened and ready for processing")
for r in range(0,dem.shape[0]):
	for c in range(0,dem.shape[1]):
		if(demValid[r][c]):
			#Calc hypCalc for this
			k = 0;
			for i in range(-1,2):
				for j in range(-1,2):
					if( not (i == 0 and j== 0) ):
						if( (r-i)<0 or (r-i)>=dem.shape[0] or (c-j)<0 or (c-j)>=dem.shape[1] or  not demValid[r-i][c-j]):
							hypCalc[r][c][k] = L_arr[(abs(i) + abs(j))%2]
							k = k + 1
						else:
							hypCalc[r][c][k] = ((dem[r][c] - dem[r-i][c-j])**2 + L_arr[(abs(i) + abs(j))%2] ** 2 ) ** 0.5
							k = k + 1
for r in range(0,dem.shape[0]):
	for c in range(0,dem.shape[1]):
		if(demValid[r][c]):
			#Find and store a1s 
			a1_array = np.zeros(8)

			if(r-1 >= 0):
				if(demValid[r-1][c]):
					a1_array[0:2] = hypCalc[r-1][c][3:5]
				else:
					a1_array[0:2] = [L,L]
			else:
				a1_array[0:2] = [L,L]
				
			if(c+1 < dem.shape[1]):
				if(demValid[r][c+1]):
					a1_array[2] = hypCalc[r][c+1][1]
					a1_array[3] = hypCalc[r][c+1][6]
				else:
					a1_array[2:4] = [L,L]
			else:
				a1_array[2:4] = [L,L]

			if(r+1 < dem.shape[0]):
				if(demValid[r+1][c]):
					a1_array[4] = hypCalc[r+1][c][4]
					a1_array[5] = hypCalc[r+1][c][3]
				else:
					a1_array[4:6] = [L,L]
			else:
				a1_array[4:6] = [L,L]

			if(c-1 >= 0 ):
				if(demValid[r][c-1]):
					a1_array[6] = hypCalc[r][c-1][6]
					a1_array[7] = hypCalc[r][c-1][1]
				else:
					a1_array[6:] = [L,L]
			else:
				a1_array[6:] = [L,L]
			
			k = 0;
			for i in range(-1,2):
				for j in range(-1,2):
					if( not (i == 0 and j== 0) ):
						c1 = hypCalc[r][c][ordArray[k]] / 2.0

						b1 = hypCalc[r][c][ ordArray[(k+1) % 8] ] / 2.0
						a1 = a1_array[k] / 2.0
						#Divide by 2 to ensure area isn't calculated twice.
						s = (a1 + b1 + c1 )/ 2.0
						#print(s)
						#print(a1)
						#print(b1)
						#print(c1)
						test = s * (s-a1) * (s-b1) * (s-c1)
						if(test > 0):
							surfAreaDiv[r][c][k] = math.sqrt(test )
						k = k + 1
			surfArea[r][c] = sum(surfAreaDiv[r][c])
print(surfArea[1000][1000])
print("Processing Done.")
im = Image.fromarray(surfArea)
im.save('./Area5_act2.tif')
imsave('./Area5_err2.tif',surfArea)




