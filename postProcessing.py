# POSTGIS AUTOMATED CODE
import os
import subprocess
import tkinter
from tkinter import filedialog

# PATH
scripts = "D:\\scripts\\processes\\create_colorized_dem.py"
color_txt_file = "D:\\scripts\\python\\dem_histogram_colorize\\colour-relief-tharangini-loc.txt"
local_2_global_py = "C:\\Users\\user\\Desktop\\GitHub\\scripts\\python\\bin\\local2global.py"
local_2_global_csv = "C:\\Users\\user\\Desktop\\GitHub\\scripts\\python\\raster_processing\\local2global.csv"

root = tkinter.Tk()
root.withdraw() #use to hide tkinter window

# PHOTOSCAN OUTPUTS PATH
photoscan_output_path = filedialog.askdirectory(title = "SPECIFY PHOTOSCAN OUTPUT PATH")
photoscan_output_path+='/'

# ASSIGN THE COORDINATE TO THE PHOTOSCAN OUTPUT DEM & ORTHOMOSAIC AND SAVE INTO OUTPUTS FOLDER
outputs_path = filedialog.askdirectory(title = "SPECITY OUTPUTS PATH")
outputs_path+='/'
for ras in [f for f in os.listdir(photoscan_output_path) if '.tif' in f]:
    outputs_data = outputs_path + ras.replace('.tif', '_utm.tif')
    subprocess.call('gdal_translate -a_srs EPSG:32643 "%s" "%s"'%(photoscan_output_path + ras, outputs_data))

# CLIP THE DEM & ORTHOMOSAIC ACCORDING TO AOI AND SAVE IT TO CLIPPED FOLDER

os.chdir(outputs_path)
os.mkdir('clipped')
os.chdir('clipped')
clipped_path = os.getcwd()
clipped_path+='/'

shape_path = filedialog.askopenfilename(title = "SPECIFY AOI")
for outputs in [f for f in os.listdir(outputs_path) if '.tif' in f]:
    clipped_data = clipped_path + outputs.replace('.tif', '_clipped.tif')
    subprocess.call('gdalwarp -q -cutline "%s" -crop_to_cutline "%s" "%s"' %(shape_path, outputs_path + outputs, clipped_data))

# COLORIZE THE DEM
for dem in [f for f in os.listdir(clipped_path) if 'dem' in f]:
    subprocess.call('python "%s" "%s" "%s"' %(scripts, color_txt_file, clipped_path+dem))

# COMPRESS THE CLIPPED ORTHOMOSAIC & COLORIZE DEM
for data in [f for f in os.listdir(clipped_path)]:
    compressed_data = clipped_path + data.replace('.tif', '_cmp.tif')
    if ('orthomosaic' in data):
        subprocess.call('gdal_translate -co compress=jpeg -co tiled=yes "%s" "%s"' %(clipped_path+data, compressed_data))
    elif ('crhs' in data):
        subprocess.call('gdalwarp -srcnodata 0 -dstalpha -co compress=jpeg -co tiled=yes "%s" "%s"' %(clipped_path+data, compressed_data))  

# # CONVERT LOCAL TO GLOBAL COORDINATES

os.chdir(clipped_path)
os.mkdir('global')
os.chdir('global')
global_path = os.getcwd()
global_path+='/'

for cl_data in [f for f in os.listdir(clipped_path) if "crhs.tif" in f or "clipped.tif" in f]:
    subprocess.call('python "%s" --name tharangini "%s" "%s"' %(local_2_global_py, local_2_global_csv, clipped_path+cl_data))

# GLOBAL DATA MOVE TO GLOBAL FOLDER
for global_ras in [f for f in os.listdir(clipped_path) if '_global.tif' in f]:
    subprocess.call('mv "%s" "%s"' %((clipped_path+global_ras), global_path))

# COMPRESS GLOBAL DATA    
for global_data in [f for f in os.listdir(global_path)]:
    global_compressed_data = global_path + global_data.replace('.tif', '_cmp.tif')
    if ('orthomosaic' in global_data):
        subprocess.call('gdal_translate -co compress=jpeg -co tiled=yes "%s" "%s"' %(global_path+global_data, global_compressed_data))
    elif('crhs' in global_data):
        subprocess.call('gdalwarp -srcnodata 0 -dstalpha -co compress=jpeg -co tiled=yes "%s" "%s"' %(global_path+global_data, global_compressed_data))







