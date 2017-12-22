import os
import subprocess
import tkinter
from tkinter import filedialog
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

create_colorized_dem_script = os.getcwd() + "/create_colorized_dem.py"
local_2_global_path = os.getcwd() + "/local2global.py"

# INPUTS
project_name = "nice_quarry" 

root = tkinter.Tk()
root.withdraw() #use to hide tkinter window

# PHOTOSCAN OUTPUTS PATH
photoscan_output_path = filedialog.askdirectory(title = "SPECIFY PHOTOSCAN OUTPUT PATH")
photoscan_output_path+='/'

# ASSIGN THE COORDINATE TO THE PHOTOSCAN OUTPUT DEM & ORTHOMOSAIC AND SAVE INTO OUTPUTS FOLDER
logging.info("ASSIGN COORDINATE")
outputs_path = filedialog.askdirectory(title = "SPECITY OUTPUTS PATH")
outputs_path+='/'
for ras in [f for f in os.listdir(photoscan_output_path) if '.tif' in f]:
    outputs_data = outputs_path + ras.replace('.tif', '_utm.tif')
    subprocess.call('gdal_translate -a_srs EPSG:32643 "%s" "%s"'%(photoscan_output_path + ras, outputs_data))

# CLIP THE DEM & ORTHOMOSAIC ACCORDING TO AOI AND SAVE IT TO CLIPPED FOLDER
logging.info("CLIPPING PROCESS")
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
logging.info("COLORIZATION OF DEM")
color_txt_file = filedialog.askopenfilename(title = "SPECIFY COLOR RAMP TEXT FILE")
for dem in [f for f in os.listdir(clipped_path) if 'dem' in f]:
    subprocess.call('python "%s" "%s" "%s"' %(create_colorized_dem_script, color_txt_file, clipped_path+dem))

# COMPRESS THE CLIPPED ORTHOMOSAIC & COLORIZE DEM
logging.info("COMPRESSING CLIPPED FOLDER FILE")
for data in [f for f in os.listdir(clipped_path)]:
    compressed_data = clipped_path + data.replace('.tif', '_cmp.tif')
    if ('orthomosaic' in data):
        subprocess.call('gdal_translate -co compress=jpeg -co tiled=yes "%s" "%s"' %(clipped_path+data, compressed_data))
    elif ('crhs' in data):
        subprocess.call('gdalwarp -srcnodata 0 -dstalpha -co compress=jpeg -co tiled=yes "%s" "%s"' %(clipped_path+data, compressed_data))  

# # CONVERT LOCAL TO GLOBAL COORDINATES
logging.info("LOCAL TO GLOBAL CONVERSION")
local_2_global_csv = filedialog.askopenfilename(title = "SPECIFY LOCAL 2 GLOBAL CONVERSION CSV FILE")
os.chdir(clipped_path)
os.mkdir('global')
os.chdir('global')
global_path = os.getcwd()
global_path+='/'

for cl_data in [f for f in os.listdir(clipped_path) if "crhs.tif" in f or "clipped.tif" in f]:
    subprocess.call('python "%s" --name %s "%s" "%s"' %(local_2_global_path, project_name, local_2_global_csv, clipped_path+cl_data))

# GLOBAL DATA MOVE TO GLOBAL FOLDER
logging.info("MOVING GLOBAL FILE TO GLOBAL FOLDER")
for global_ras in [f for f in os.listdir(clipped_path) if '_global.tif' in f]:
    subprocess.call('mv "%s" "%s"' %((clipped_path+global_ras), global_path))

# COMPRESS GLOBAL DATA
logging.info("COMPRESSING GLOBAL FOLDER FILE")
for global_data in [f for f in os.listdir(global_path)]:
    global_compressed_data = global_path + global_data.replace('.tif', '_cmp.tif')
    if ('orthomosaic' in global_data):
        subprocess.call('gdal_translate -co compress=jpeg -co tiled=yes "%s" "%s"' %(global_path+global_data, global_compressed_data))
    elif('crhs' in global_data):
        subprocess.call('gdalwarp -srcnodata 0 -dstalpha -co compress=jpeg -co tiled=yes "%s" "%s"' %(global_path+global_data, global_compressed_data))







