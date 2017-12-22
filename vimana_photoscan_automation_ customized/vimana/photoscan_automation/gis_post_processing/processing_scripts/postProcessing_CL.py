import os
import subprocess
import sys
import ntpath
import shutil
import logging
import argparse

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def initialize_structure():
    try:
        # create necessary folders for execution
        required_paths = [
            photoscan_output_path + "/outputs",
            photoscan_output_path + "/outputs/clipped",
            photoscan_output_path + "/outputs/clipped/global"
        ]

        for required_directory in required_paths:
            if not os.path.exists(required_directory):
                os.makedirs(required_directory)
    except Exception as e:
        raise Exception("Error while initializing structure!" + str(e))


def get_files_by_name(name=None, directory_path=None):
    file_list = []
    if not name or not directory_path:
        sys.exit(1)
    else:
        for each_files in [file_name for file_name in os.listdir(directory_path) if name in file_name]:
            file_list.append(each_files)

    return file_list
    

def assign_coordinate(coordinate_standard=None):
    try:
        if not coordinate_standard:
            sys.exit(1)
        photoscan_output_files = get_files_by_name(".tif", photoscan_output_path)
        for each_files in photoscan_output_files:
            outputs_data = outputs_path + each_files.replace('.tif', '_utm.tif')
            subprocess.call('gdal_translate -a_srs {} "{}" "{}"'.format(
                coordinate_standard, photoscan_output_path + each_files, outputs_data))
    except Exception as e:
        raise Exception("Error while assigning coordinate!" + str(e))


def clip_files():
    try:
        # CLIP THE DEM & ORTHOMOSAIC ACCORDING TO AOI AND SAVE IT TO CLIPPED FOLDER
        utm_files = get_files_by_name(".tif", outputs_path)
        for each_files in utm_files:
            clipped_data = clipped_path + each_files.replace('.tif', '_clipped.tif')
            subprocess.call('gdalwarp -q -cutline "{}" -crop_to_cutline "{}" "{}"'.format(
                area_of_interest_file, outputs_path + each_files, clipped_data))
    except Exception as e:
        raise Exception("Error while clipping files!" + str(e))


def colorize_dem():
    try:
        dem_files = get_files_by_name("dem", clipped_path)
        for each_files in dem_files:
            subprocess.call('python "{}" "{}" "{}"'.format(
                create_colorized_dem_script, color_txt_file, clipped_path+each_files))
    except Exception as e:
        raise Exception("Error while Colorizing DEM!" + str(e))


def compress_file(directory_path=None):
    try:
        # COMPRESS THE FILE
        cmp_files = get_files_by_name(".tif", directory_path)
        for each_files in cmp_files:
            compressed_file = clipped_path + each_files.replace('.tif', '_cmp.tif')
            if 'mosaic' in each_files:
                subprocess.call('gdalwarp -srcnodata 0 -co compress=jpeg -co tiled=yes "{}" "{}"'.format(
                    directory_path + each_files, compressed_file))
            elif 'crhs' in each_files:
                subprocess.call('gdalwarp -srcnodata 0 -dstalpha -co compress=jpeg -co tiled=yes "{}" "{}"'.format(
                    directory_path + each_files, compressed_file))
    except Exception as e:
        raise Exception("Error while compressing files!" + str(e))


def global_convn(directory_path=None):
    try:
        # Local to global conversion
        global_conversion_file = get_files_by_name(".tif", directory_path)
        for each_file_path in [f for f in global_conversion_file if "crhs.tif" in f or "clipped.tif" in f]:
            subprocess.call('python "{}" --name {} "{}" "{}"'.format(
                local_2_global_path, PROJECT_NAME, local_2_global_file, clipped_path + each_file_path))
    except Exception as e:
        raise Exception("Error while Global conversion!" + str(e))


def move_file():
    try:
        global_filename_list = get_files_by_name("global", clipped_path)
        for each_file_name in global_filename_list:
            shutil.move(clipped_path+each_file_name, global_path)
    except Exception as e:
        raise Exception("Error while Moving Files!" + str(e))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Arguments for PROJECT BASE PATH, PROJECT NAME & COORDINATE STANDARD")
    parser.add_argument("-p", "--project_path", help="Local or GCloud Project Path", required=True)
    parser.add_argument("-n", "--project_name", help="Project Name", required=True)
    parser.add_argument("-c", "--coordinate_standard", help="World standard project coordinate", required=True)
    args = vars(parser.parse_args())

    PROJECT_BASE_PATH = args['project_path']
    PROJECT_NAME = args['project_name']
    COORDINATE_STANDARD = args['coordinate_standard']

    create_colorized_dem_script = os.getcwd() + "/create_colorized_dem.py"
    local_2_global_path = os.getcwd() + "/local2global.py"

    # THESE THREE FILE WE NEED TO SPECIFY
    color_txt_file = PROJECT_BASE_PATH + "/Input/colour-file.txt"
    local_2_global_file = PROJECT_BASE_PATH + "/Input/local2global.csv"
    area_of_interest_file = PROJECT_BASE_PATH + "/Input/aoi_shape.shp"
    
    photoscan_output_path = PROJECT_BASE_PATH + "/output/"

    outputs_path = photoscan_output_path + "outputs/"
    clipped_path = outputs_path + "clipped/"
    global_path = clipped_path + "global/"

    try:
        initialize_structure()
        logging.info("ASSIGN COORDINATE")
        assign_coordinate(coordinate_standard=COORDINATE_STANDARD)
        logging.info("CLIPPING PROCESS")
        clip_files()
        logging.info("COLORIZATION OF DEM")
        colorize_dem()
        logging.info("LOCAL TO GLOBAL CONVERSION")
        global_convn(clipped_path)
        logging.info("COMPRESSING CLIPPED FOLDER FILE")
        compress_file(clipped_path)
        logging.info("COMPRESSING GLOBAL FOLDER FILE")
        compress_file(global_path)
        logging.info("MOVING GLOBAL FILE TO GLOBAL FOLDER")
        move_file()
    except Exception as e:
        raise Exception("Error during post processing!" + str(e))
