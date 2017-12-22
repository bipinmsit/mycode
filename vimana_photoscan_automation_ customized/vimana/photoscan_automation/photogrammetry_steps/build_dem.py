import logging

from vimana.photoscan_automation.photogrammetry_steps.base_steps import PhotogrammetryStep, PhotoScan
from vimana.photoscan_automation.photogrammetry_workflow import current_utc_datetime


class BuildDEM(PhotogrammetryStep):
    """
    we'll build DEM here
    """

    def __init__(self, workflow_object):
        super().__init__(workflow_object)
        self.minimum_number_of_point_projection = 1
        self.reprojection_error_threshold = 10
        self.interpolation = PhotoScan.EnabledInterpolation
        self.source = PhotoScan.DenseCloudData
        self.start_time = current_utc_datetime()

    def check_prerequisites(self):
        logging.debug("Checking prerequisite")

    def read_params(self):
        logging.debug("Reading params")

    def open_project(self):
        self.open_project_util(project_type='psx')

    def execute(self):
        logging.info(" Build DEM - Started  " + str(current_utc_datetime()))

        # set merge chunk as current chunk if split chunk is executed
        if self.workflow_object.split_into_chunk:
            self.set_current_chunk("Merged Chunk")

        if "build_dem" in self.workflow_object.config:
            if self.workflow_object.config["build_dem"]["source"] == "DenseCloudData":
                self.source = PhotoScan.DenseCloudData
            elif self.workflow_object.config["build_dem"]["source"] == "PointCloudData":
                self.source = PhotoScan.PointCloudData
            elif self.workflow_object.config["build_dem"]["source"] == "DepthMapsData":
                self.source = PhotoScan.DepthMapsData
            elif self.workflow_object.config["build_dem"]["source"] == "ModelData":
                self.source = PhotoScan.ModelData
            elif self.workflow_object.config["build_dem"]["source"] == "TiledModelData":
                self.source = PhotoScan.TiledModelData
            elif self.workflow_object.config["build_dem"]["source"] == "OrthomosaicData":
                self.source = PhotoScan.OrthomosaicData

            if self.workflow_object.config["build_dem"]["interpolation"] == "EnabledInterpolation":
                self.interpolation = PhotoScan.EnabledInterpolation
            elif self.workflow_object.config["build_dem"]["interpolation"] == "ExtrapolatedInterpolation":
                self.interpolation = PhotoScan.ExtrapolatedInterpolation
            elif self.workflow_object.config["build_dem"]["interpolation"] == "DisabledInterpolation":
                self.interpolation = PhotoScan.DisabledInterpolation

            #self.coordinateSystem = self.workflow_object.config["build_dem"]["coordinate_system"]
            self.reprojection_error_threshold = 10

        self.workflow_object.doc.chunk.buildDem(self.source, self.interpolation)
        logging.info(" Build DEM - Finished  " + str(current_utc_datetime()))

    def export(self):
        """
        We'll export DEM here
        :return:
        """

        # Added functionality for user to control export Coordinate System
        if "build_dem" in self.workflow_object.config:
            user_crs = self.workflow_object.config["build_dem"]["coordinate_system"]
            if user_crs == "EPSG::9001":
                user_crs = self.workflow_object.doc.chunk.crs
            else:
                user_crs = PhotoScan.CoordinateSystem(str(user_crs))

        self.workflow_object.doc.chunk.exportDem(self.workflow_object.doc_dem, format=PhotoScan.RasterFormatTiles,
                                             image_format=PhotoScan.ImageFormatTIFF,
                                             projection=user_crs, write_kml=False,
                                             write_world=False, tiff_big=True)
        logging.debug("Exporting results")
        step = {'params': {}}
        step['params']['build_dem'] = {}
        step['params']['buildPoints'] = {}
        step['params']['build_dem']['source'] = str(self.source)
        step['params']['build_dem']['interpolation'] = str(self.interpolation)
        step['params']['buildPoints']['error'] = str(self.reprojection_error_threshold)
        step['exports'] = {}
        step['exports']['DEM'] = str(self.workflow_object.doc_dem)
        self.export_step_state_details("BuildDEM", step)