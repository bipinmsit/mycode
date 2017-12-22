import os
import ogr
import osr
import csv
import json
import numpy as np
import gdal
from raster_processing.raster_chunks import GeoChunks as gc
driverName = "ESRI Shapefile"


def define_lines(point_arr):
    lines = []
    for i in range(point_arr.shape[0]-1):
        temp = []
        start_point = point_arr[i]
        end_point = point_arr[(i+1)%point_arr.shape[0]]
        line_vec = end_point - start_point
        unit_vec = line_vec / np.linalg.norm(line_vec)
        temp.append(unit_vec)
        temp.append(line_vec)
        temp.append([start_point, end_point])
        lines.append(temp)

    return lines


def poly_as_points(polygon_file, points_file, samp_dist=0.1, UTM_EPSG=32643):
    """
    Function to create sampling points along a polygon that defines a shape.
    polygon_file -> File path to input vector polygon.shp file
    points_file -> File path to output vector points.shp file
    samp_dist -> Sampling distance in metres which controls the distance between adjacent points
    UTM_EPSG -> EPSG code for CRS in UTM, for that particular site.
                Default set to 32643, which is the UTM for Bangalore(Zone 43N)

    """
    driver = ogr.GetDriverByName(driverName)
    data = driver.Open(polygon_file)
    #Note that layers are 0-indexed unlike raster bands in gdal
    input_layer = data.GetLayerByIndex(0)
    in_srs = osr.SpatialReference()
    in_EPSG = int(input_layer.GetSpatialRef().GetAttrValue("AUTHORITY", 1))
    in_srs.ImportFromEPSG(in_EPSG)
    ftr_count = input_layer.GetFeatureCount()
    if os.path.exists(points_file):
        print("Specified output file already exists.\n"\
        "Deleting current file and replaing it with new points file")
        driver.DeleteDataSource(points_file)
    point_data_src = driver.CreateDataSource(points_file)
    out_srs = osr.SpatialReference()
    out_srs.ImportFromEPSG(UTM_EPSG)
    out_layer = point_data_src.CreateLayer("points_layer", out_srs,ogr.wkbPoint)
    field_id = ogr.FieldDefn("id", ogr.OFTInteger)
    out_layer.CreateField(field_id)

    #If the input vector layer is not in the same coordinate system as the output
    #UTM EPSG, then we have to reproject the input points accordingly.
    coordTransform = None
    if in_srs != out_srs:
        print("Warning: Input and output layer have different projection systems\n"\
                "\tThis could lead to possible errors.")
        coordTransform = osr.CoordinateTransformation(in_srs, out_srs)

    point_count = 0
    for ftr in input_layer:
        geom = ftr.GetGeometryRef()
        if coordTransform is None:
            pass
        else:
            #Reprojecting points to out_srs
            geom.Transform(coordTransform)
        geomJson = json.loads(geom.ExportToJson())
        for k in range(geom.GetGeometryCount()):
            polyRingArr = np.array(geomJson['coordinates'][k])
            #Converting the Polygon to line segments
            polyLines = define_lines(polyRingArr)
            for j in range(len(polyLines)):
                unit_samp_vector = polyLines[j][0] * samp_dist
                start_point = polyLines[j][2][0]
                line_vector = polyLines[j][1]
                num_lines = int(np.floor(np.linalg.norm(line_vector) \
                            / np.linalg.norm(unit_samp_vector)))

                # Creating a point at the start of every line segment
                feature = ogr.Feature(out_layer.GetLayerDefn())
                feature.SetField("id", point_count)
                point_count += 1
                temp_point = start_point
                wkt = "POINT(%f %f)" % (temp_point[0], temp_point[1])
                point = ogr.CreateGeometryFromWkt(wkt)
                feature.SetGeometry(point)
                out_layer.CreateFeature(feature)
                feature = None

                for i in range(num_lines):
                    feature = ogr.Feature(out_layer.GetLayerDefn())
                    feature.SetField("id", point_count)
                    point_count += 1
                    temp_point = start_point + unit_samp_vector*i
                    wkt = "POINT(%f %f)" % (temp_point[0], temp_point[1])
                    point = ogr.CreateGeometryFromWkt(wkt)
                    feature.SetGeometry(point)
                    out_layer.CreateFeature(feature)
                    feature = None


        point_data_src = None


def lines_as_points(polygon_file, points_file, samp_dist=0.1, UTM_EPSG=32643):
    """
    Function to create sampling points along a polygon that defines a shape.
    polygon_file -> File path to input vector polygon.shp file
    points_file -> File path to output vector points.shp file
    samp_dist -> Sampling distance in metres which controls the distance between adjacent points
    UTM_EPSG -> EPSG code for CRS in UTM, for that particular site.
                Default set to 32643, which is the UTM for Bangalore(Zone 43N)

    """
    driver = ogr.GetDriverByName(driverName)
    data = driver.Open(polygon_file)
    #Note that layers are 0-indexed unlike raster bands in gdal
    input_layer = data.GetLayerByIndex(0)
    in_srs = osr.SpatialReference()
    in_EPSG = int(input_layer.GetSpatialRef().GetAttrValue("AUTHORITY", 1))
    in_srs.ImportFromEPSG(in_EPSG)
    ftr_count = input_layer.GetFeatureCount()
    if os.path.exists(points_file):
        print("Specified output file already exists.\n"\
        "Deleting current file and replaing it with new points file")
        driver.DeleteDataSource(points_file)
    point_data_src = driver.CreateDataSource(points_file)
    out_srs = osr.SpatialReference()
    out_srs.ImportFromEPSG(UTM_EPSG)
    out_layer = point_data_src.CreateLayer("points_layer", out_srs, ogr.wkbPoint)
    field_id = ogr.FieldDefn("id", ogr.OFTInteger)
    out_layer.CreateField(field_id)

    #If the input vector layer is not in the same coordinate system as the output
    #UTM EPSG, then we have to reproject the input points accordingly.
    coordTransform = None
    if in_EPSG != UTM_EPSG:
        print("Warning: Input and output layer have different projection systems\n"\
                "\tThis could lead to possible errors.")
        coordTransform = osr.CoordinateTransformation(in_srs, out_srs)

    point_count = 0
    for ftr in input_layer:
        geom = ftr.GetGeometryRef()
        if coordTransform is None:
            pass
        else:
            #Reprojecting points to out_srs
            geom.Transform(coordTransform)
        geomJson = json.loads(geom.ExportToJson())
        polyRingArr = np.array(geomJson['coordinates'])
        #Converting the Polygon to line segments
        polyLines = define_lines(polyRingArr)

        for j in range(len(polyLines)):
            unit_samp_vector = polyLines[j][0] * samp_dist
            start_point = polyLines[j][2][0]
            line_vector = polyLines[j][1]
            num_lines = int(np.floor(np.linalg.norm(line_vector)\
                        / np.linalg.norm(unit_samp_vector)))

            # Creating a point at the start of every line segment
            feature = ogr.Feature(out_layer.GetLayerDefn())
            feature.SetField("id", point_count)
            point_count += 1
            temp_point = start_point
            wkt = "POINT(%f %f)" % (temp_point[0], temp_point[1])
            point = ogr.CreateGeometryFromWkt(wkt)
            feature.SetGeometry(point)
            out_layer.CreateFeature(feature)
            feature = None

            for i in range(num_lines):
                feature = ogr.Feature(out_layer.GetLayerDefn())
                feature.SetField("id", point_count)
                point_count += 1
                temp_point = start_point + unit_samp_vector*i
                wkt = "POINT(%f %f)" % (temp_point[0], temp_point[1])
                point = ogr.CreateGeometryFromWkt(wkt)
                feature.SetGeometry(point)
                out_layer.CreateFeature(feature)
                feature = None

    point_data_src = None
        

def points_as_csv(points_file,csv_file):
    """
    Function to store the feature of the points file, in a csv file, for further processing
    Note that the Points file must be a ' *.shp ' file
    """
    #Setting up to read, and write to file
    driver = ogr.GetDriverByName(driverName)
    data_src = driver.Open(points_file)
    csv_src = open(csv_file,'w')
    csv_writer = csv.writer(csv_src)

    #Getting field names from the Points file
    layer = data_src.GetLayerByIndex(0)
    layer.GetFeatureCount()
    f = layer[0]
    field_names = []
    for i in range(f.GetFieldCount()):
        field_names.append(f.GetFieldDefnRef(i).GetName())
    field_names.append("Longitude/Easting")
    field_names.append("Latitude/Northing")
    #Writing Header Row to CSV
    csv_writer.writerow(field_names)
    for ftr in layer:
        r = []
        for i in range(ftr.GetFieldCount()):
            r.append(ftr.GetField(i))
        geom_json = json.loads(ftr.geometry().ExportToJson())
        for i in range(2):
            r.append(geom_json['coordinates'][i])
        csv_writer.writerow(r)
    csv_src.close()

def vol_from_points(dem_file, points_file, vol_dem = None, plane_out='./out_dem_plane.tif'):
    """
    dem_file        -> DEM to sample points from, to create the plane.
    points_file     -> Points File used to specify where to sample the DEM values.
    vol_dem         -> DEM to find Volume wrt Plane. If no value is given, then volume is found 
                       wrt to dem_file
    plane_out       -> The output raster created based on the plane. 
    Function to find the volume of a DEM based on points defined on its boundary.
    This is done by sampling the DEM at the specified points, and using the (x,y,z) coordinates 
    to fit a plane using SVD. SVD gives us the normal, and the means along each axis, using which 
    we can find the plane's Z value for every corresponding (x,y) pair in the DEM.
    """
    driver = ogr.GetDriverByName(driverName)
    dem = gc(dem_file)
    points_data = driver.Open(points_file)
    dem_band = dem.data_bands[0]
    p_layer = points_data.GetLayerByIndex(0)
    print('Raster projection is ')
    dem_srs = osr.SpatialReference()
    dem_srs.ImportFromWkt(dem.data_gtif.GetProjectionRef())
    raster_EPSG = int(dem_srs.GetAttrValue('AUTHORITY',1))
    print(raster_EPSG)

    print('Points file projection is ')
    points_srs = p_layer.GetSpatialRef()
    points_EPSG = int(points_srs.GetAttrValue('AUTHORITY',1))
    print(points_EPSG)
    coordTransform = None
    if raster_EPSG != points_EPSG:
        print('Warning. Coordinate Systems are not the same. Sampling could give wrong values.\n'\
              'Do not proceed with sampling')
        coordTransform = osr.CoordinateTransformation(points_srs,dem_srs)
    #Coordinates of the Upper Left corner of the raster
    
    ulx = dem.geo_trans[0]
    uly = dem.geo_trans[3]
    x_arr = []
    y_arr = []
    z_arr = []

    for i in range(p_layer.GetFeatureCount()):
        ftr = p_layer[i]
        geom = ftr.GetGeometryRef()
        if(coordTransform is None):
            pass
        else:
            #Reprojecting points to out_srs
            geom.Transform(coordTransform)
        geomJSON = json.loads(geom.ExportToJson())
        p_val = geomJSON['coordinates']
        x_arr.append(p_val[0])
        y_arr.append(p_val[1])
        p_val = [p_val[0] - ulx, p_val[1] - uly]
        crds = np.array(p_val)/[dem.geo_trans[1],dem.geo_trans[5]]
        z_val = dem_band.ReadAsArray(int(np.floor(crds[0])),int(np.floor(crds[1])),1,1)
        z_arr.append(z_val)
    
    X_arr = np.array(x_arr)
    Y_arr = np.array(y_arr)
    Z_arr = np.array(z_arr)
    Z_arr = Z_arr.reshape((len(x_arr)))
    Xm = np.mean(X_arr)
    Ym = np.mean(Y_arr)
    Zm = np.mean(Z_arr)
    i_arr = np.dstack((X_arr - Xm,Y_arr - Ym, Z_arr - Zm))
    i2_arr = i_arr.reshape((len(x_arr),3))
    u,s,v = np.linalg.svd(i2_arr)
    _v = np.linalg.inv(v)
    _n = np.zeros((3,1))
    _n[2] = 1
    _out = np.matmul(_v,_n).reshape((3))
    #Function to calculate Z on the plane, given x,y 
    Z_func = lambda a,b: ((Xm - a)*_out[0] + (Ym - b)*_out[1])/_out[2] + Zm
    
    if vol_dem is None:
        ref_dem = dem
    else:
        ref_dem = gc(vol_dem)

    plane = gc.create_from(ref_dem,plane_out)
    v_sum = []
    for ch in ref_dem.break_chunks(chunk_x=1000,chunk_y=1000):
        ref_dem_arr = ref_dem.read(chunk=ch)
        mask = np.where(ref_dem_arr == ref_dem.no_data_value)
        new_arr = np.ones(ref_dem_arr.shape) * plane.no_data_value
        for x in range(ref_dem_arr.shape[1]):
            for y in range(ref_dem_arr.shape[0]):
                if(ref_dem_arr[y,x] == ref_dem.no_data_value):
                    new_arr[y,x] = plane.no_data_value
                else:
                    _x = x + ch[0]
                    _y = y + ch[1]
                    xc = ref_dem.geo_trans[0] + _x * ref_dem.geo_trans[1]
                    yc = ref_dem.geo_trans[3] + _y * ref_dem.geo_trans[5]
                    _z = Z_func(xc,yc)
                    new_arr[y,x] = np.float(_z)
                   
                    v_sum.append(_z - ref_dem_arr[y,x])
                    
        #_z_sum = np.sum(new_arr[np.where(new_arr != plane.no_data_value)])
        #_d_sum = np.sum(ref_dem_arr[np.where(ref_dem_arr != ref_dem.no_data_value)])
      
        print(ch)
        plane.x_chunk_size=1000
        plane.y_chunk_size=1000
        plane.write(new_arr,chunk=ch)
    
    V2_sum = np.array(v_sum)
    Vol = np.sum(V2_sum) * ref_dem.geo_trans[1] ** 2
    print('Volume with reference to the plane is ' + str(Vol) + '\n')
    return Vol,[Xm,Ym,Zm],_out
                        


    

    


