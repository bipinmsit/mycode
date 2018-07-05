import argparse
import  subprocess
import logging
import gdal
import csv
import numpy as np
import os
from osgeo import ogr
from osgeo import osr

logging.basicConfig(level=logging.DEBUG)

def downsample_dtm(pix_x, pix_y, in_dtm):
    downsampled_dtm = in_dtm.replace('.tif', '_downsampled_by_%s_%s.tif' %(pix_x, pix_y))
    subprocess.call("gdalwarp -tr %s %s %s %s" %(pix_x, pix_y, in_dtm, downsampled_dtm))
    print("Downsampled DTM is saved at %s" %downsampled_dtm)
    return downsampled_dtm

def raster_to_point(downsampled_dtm, pix_x, pix_y, in_dtm):
    data =gdal.Open(downsampled_dtm)
    data_arr = data.ReadAsArray()
    data_extent = data.GetGeoTransform()
    coords_list = []
    for i in range(data.RasterXSize):
        for j in range(data.RasterYSize):
            x_coord = data_extent[0] + i * data_extent[1]
            y_coord = data_extent[3] + j * data_extent[5]
            z_value = data_arr[j][i]
            coords_list.append([((0.5 * float(pix_x)) + x_coord), (y_coord - (0.5 * float(pix_y))), z_value])
    coords_list = np.array(coords_list)
    final_list_without_no_data = np.delete(coords_list, np.where(coords_list[:,2] == -99999.0), 0)

    dtm_path = os.path.dirname(os.path.abspath(in_dtm))

    with open(dtm_path + "\\pixel_list_%s_%s.csv" %(pix_x, pix_y), "w") as csvfile:
        writer = csv.writer(csvfile, delimiter = ",")
        writer.writerow(['Easting', 'Northing', 'Elevation'])
        for row in final_list_without_no_data:
            writer.writerow(row)

# def csv_to_shp():
    driver = ogr.GetDriverByName("ESRI Shapefile")
    data_source = driver.CreateDataSource(dtm_path + "\\dtm_%s_%s_shp.shp" %(pix_x, pix_y))
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(32643)
    layer = data_source.CreateLayer("dtm_%s_%s_shp" %(pix_x, pix_y), srs, ogr.wkbPoint)

    layer.CreateField(ogr.FieldDefn("Easting", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("Northing", ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("Elevation", ogr.OFTReal))

    with open(dtm_path + "\\pixel_list_%s_%s.csv" %(pix_x, pix_y), "r") as csvf:
        reader = csv.DictReader(csvf, delimiter = ",")
        for row in reader:
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetField("Easting", row['Easting'])
            feature.SetField("Northing", row['Northing'])
            feature.SetField("Elevation", row['Elevation'])

            wkt = "POINT(%f %f)" % (float(row['Easting']), float(row['Northing']))
            point = ogr.CreateGeometryFromWkt(wkt)
            feature.SetGeometry(point)
            layer.CreateFeature(feature)
            feature = None
        data_source = None

parser = argparse.ArgumentParser(description="Automatically creating the grid")
parser.add_argument("-px", "--Pix_X", required = True, help = "X Dimention of Pixel")
parser.add_argument("-py", "--Pix_Y", required = True, help = "Y Dimention of Pixel")
parser.add_argument("-id", "--Input_DTM", required = True, help = "Input DTM Path")
args = parser.parse_args()


if __name__ == "__main__":
    logging.info("DOWNSAMPLING THE INPUT DTM BY GIVEN PARAMETERS")
    d_dtm = downsample_dtm(args.Pix_X, args.Pix_Y, args.Input_DTM)

    logging.info("Extracting points from downsampled raster pixels")
    raster_to_point(d_dtm, args.Pix_X, args.Pix_Y, args.Input_DTM)
