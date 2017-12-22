# GIS Post Processing

# Overview

This contains steps for [GIS](https://en.wikipedia.org/wiki/Geographic_information_system) post processing which:

# Config/Pre-requisites

* Assumption Inputs from Previous Photogrammetry process:
	* Digital Elevation Model-DEM (.tif File) - present in `/Output` dir
	* Orthomosaic (.tif File) - present in `/Output`
* Requirements for this process:
	* Coordinate-System() to be used (taken as CLI argument). [How to find correct Coordinate System?]
	* Area of Interest-AOI File (aoi_shape.shp). To be available in `/Input` dir, else step fails
	* Color relief File (colour-file.txt). To be available in `/Input` dir, else step fails
	* local2Global Conversion (local2Global.csv File). To be available in `/Input` dir, else step fails

# Results

* It will create 'outputs' folder inside 'output/' that contains the assigned coordinate of photoscan outputs.
* Creates 'clipped' folder inside 'outputs/' that contains clipped, colorize and compressed file.
* Creates 'global' folder inside 'clipped/' that contains global converted & and their compressed file.

# Usage
Root Folder for execution: scripts folder This package is for triggering the work flow:


```sh
Usage: postProcessing.py [-h] [-e ENVIRONMENT]
									[-p PROJECT_PATH]
                                    [-n PROJECT_NAME]
                                    [-c COORDINATE_STANDARD]
Arguments for GIS Post Processing process.

optional arguments:
  -h, --help            show this help message and exit

-p PROJECT_PATH, --project_path PROJECT_PATH
                        Local or GCloud Project Path
  -n PROJECT_NAME, --project_name PROJECT_NAME
                        Project Name
  -c COORDINATE_STANDARD --coordinate_standard COORDINATE_STANDARD
  						World standard project coordinate
```
Example usage:

```py
python postProcessing.py
```

# Installation

* Activate Conda Env using file `scripts/python/gis_post_processing/gis_env.yml`
* set `ENV` variable `GDAL_DATA=<conda-env>env\Library\share\gdal`

# Execution Flow

* Intialize structure and create 'outputs'>'clipped'>'global' folder inside ouput.
* Assigns the world standard coordinate to DEM & Orthomosaic and save it into "outputs" folder  
* Clip it according to the shapefile and save it into "clipped" folder
* Colorize the DEM and save it into "clipped" Folder
* Convert local coordinate process data into global coordinate and save it into "clipped" folder
* Compress colorize DEM & Orthomosaic and save it into "clipped" folder
* Move all global converted data into 'global' folder
* Compress global folder containing data and save it into same folder
