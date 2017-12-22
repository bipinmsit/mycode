"""
Utility to Convert a DEM or orthomosaic from local to global coordinates.
For more information on GeoTransforms, refer:
http://www.gdal.org/gdal_datamodel.html#gdal_datamodel_dataset_gtm
"""
import raster_processing.raster_chunks as rc
import numpy as np

# Function to Translate a Point
def translate(raster, delta, rot_translate_gt=None):
    """
    Function to translate a raster by delta(x, y) amount
    Args:
        raster: Full Path to raster to be translated
        delta: The amount by which the raster is to be translated as [delta_x, delta_y]
    """
    print("Translating by delta: {}".format(delta))
    r_data = rc.GeoChunks(raster, update=True)
    # Getting GeoTransform
    if rot_translate_gt is None:
        r_gt = list(r_data.geo_trans)
    else:
        r_gt = list(rot_translate_gt)
    # Translating GeoTransform
    r_gt[0] += delta[0]
    r_gt[3] += delta[1]
    # Applying Translated GeoTransform
    new_gt = tuple(r_gt)
    r_data.data_gtif.SetGeoTransform(new_gt)
    r_data.data_gtif.FlushCache()
    r_data = None
    # Translation Done
    return 0

# Function to rotate a raster by a specified angle
def rotate(raster, angle_deg, centre_rotation=None):
    """
    Function to rotate a raster by angle_deg (degrees), with centre of rotation as origin
    (if specified)
    Args:
        raster: Full path to raster to be translated
        angle_deg: Angle in degrees by which the raster is to be rotated
        origin: The Centre of Rotation (if specified)
    """
    r_data = rc.GeoChunks(raster, update=True)
    # Getting GeoTransform
    r_gt = list(r_data.geo_trans)
    new_gt = rotate_geo_trans(angle_deg, r_gt)
    if centre_rotation is None:
        r_data.data_gtif.SetGeoTransform(new_gt)
        r_data.data_gtif.FlushCache()
    else:
        # Translation to ensure that raster is rotated about `centre_rotation`
        # Finding pixel_xy of rotation centre
        old_centre_pix_xy = get_pix_from_crds(centre_rotation, r_gt)
        new_centre_xy = np.array(get_crds_from_pix(old_centre_pix_xy, new_gt))
        centre_rotation = np.array(centre_rotation)
        delta = centre_rotation - new_centre_xy
        translate(raster, delta, new_gt)
    r_data = None
    return 0

def rotate_geo_trans(rot_angle_deg, geo_trans):
    """
    Function to rotate a GeoTransform by a given angle of rotation
    Args:
        rot_angle_deg: Angle to Rotate (in degrees)
        geo_trans: GeoTransform to rotate
    Returns:
        rot_geo_trans: Rotated GeoTransform
    """
    if isinstance(geo_trans, list):
        gt_list = geo_trans
    else:
        gt_list = list(geo_trans)
    theta = np.deg2rad(rot_angle_deg)
    rot_mat = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]]).reshape((2,2))
    gt_mat = np.array([[gt_list[1], 0.0], [0.0, gt_list[5]]]).reshape((2,2))
    rot_gt_mat = np.matmul(rot_mat, gt_mat)
    rot_geo_trans = (gt_list[0], rot_gt_mat[0, 0], rot_gt_mat[0, 1],
                     gt_list[3], rot_gt_mat[1, 0], rot_gt_mat[1, 1])
    return rot_geo_trans

def get_pix_from_crds(pt_crds, geo_trans):
    """
    Function to get pixel location of a point in a raster, given its geo-referenced location and
    the geo_transform of the raster.
    Args:
        pt_crds: Geo-referenced Location of the point, as [geo_x, geo_y]
        geo_trans: Geo_transform of the raster
    Returns:
        pixel_xy: Pixel location of the point as [pix_x, pix_y] 
    
    GeoTransform
    ----------------
    X_geo = gt[0] + X_pix * gt[1] + Y_pix * gt[2]
    Y_geo = gt[3] + X_pix * gt[4] + Y_pix * gt[5]
    """
    if isinstance(geo_trans, list):
        gt = geo_trans
    else:
        gt = list(geo_trans)
    geo_x = pt_crds[0]
    geo_y = pt_crds[1]
    # Setting up parameters for solving
    # Refer help(np.linalg.solve)
    coeff_mat = np.array([[gt[1], gt[2]],[gt[4], gt[5]]])
    ordin_mat = np.array([geo_x - gt[0], geo_y - gt[3]])
    # Solving Equation
    pt_out = np.linalg.solve(coeff_mat, ordin_mat)
    pixel_xy = [int(pt_out[0]), int(pt_out[1])]
    return pixel_xy

def get_crds_from_pix(pix_crds, geo_trans):
    """
    Function to get geo-referenced location of a point in a raster, given its pixel location and
    the geo_transform of the raster.
    Args:
        pix_crds: pixel location of the point, as [geo_x, geo_y]
        geo_trans: Geo_transform of the raster
    Returns:
        geo_xy: Pixel location of the point as [pix_x, pix_y] 
    
    GeoTransform
    ----------------
    X_geo = gt[0] + X_pix * gt[1] + Y_pix * gt[2]
    Y_geo = gt[3] + X_pix * gt[4] + Y_pix * gt[5]
    """
    if isinstance(geo_trans, list):
        gt = geo_trans
    else:
        gt = list(geo_trans)
    # Calculating Geo Location
    X_geo = gt[0] + pix_crds[0] * gt[1] + pix_crds[1] * gt[2]
    Y_geo = gt[3] + pix_crds[0] * gt[4] + pix_crds[1] * gt[5]
    geo_xy = [X_geo, Y_geo]
    return geo_xy

def angle_between_vec(local_vec, global_vec):
    """
    Find angle between 2 vectors
    """
    dot_prod = np.linalg.norm(np.dot(local_vec, global_vec))
    denom = np.linalg.norm(local_vec) * np.linalg.norm(global_vec)
    np.arccos(dot_prod/denom)
    rad = np.arccos(dot_prod/denom)
    return np.rad2deg(rad)

class Point():
    """
    Class to simplify access to point data
    Params:
        local_crds: Local Coordinates of the Point as [Long, Lat]
        global_crds: Global Coordinates of the Point as [Long. Lat]
    """
    local_crds  = None
    global_crds = None
    def __init__(self, arr):
        self.local_crds = np.array(arr[1:3])
        self.global_crds = np.array(arr[3:5])
 

