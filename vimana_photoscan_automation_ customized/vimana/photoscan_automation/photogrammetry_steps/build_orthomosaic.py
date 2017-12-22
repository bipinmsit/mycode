import logging

from vimana.photoscan_automation.photogrammetry_steps.base_steps import show_progress, PhotogrammetryStep, PhotoScan
from vimana.photoscan_automation.photogrammetry_workflow import current_utc_datetime


class BuildOrthomosaic(PhotogrammetryStep):
    """
    we'll build the Orthomosaic here
    """

    def __init__(self, workflow_object):
        super().__init__(workflow_object)
        self.color_correction = False
        self.fill_holes = True
        self.blending = PhotoScan.BlendingMode.MosaicBlending
        self.surface = PhotoScan.DataSource.ModelData
        self.start_time = current_utc_datetime()

    def check_prerequisites(self):
        logging.debug("Checking prerequisite")

    def read_params(self):
        logging.debug("Reading params")

    def open_project(self):
        self.open_project_util(project_type='psx')

    def execute(self):
        logging.info(" Build OrthoMosaic - Started  " + str(current_utc_datetime()))

        # set merge chunk as current chunk if split chunk is executed
        if self.workflow_object.split_into_chunk:
            self.set_current_chunk("Merged Chunk")

        if "build_orthomosaic" in self.workflow_object.config:
            if self.workflow_object.config["build_orthomosaic"]["surface"] == "ModelData":
                self.surface = PhotoScan.DataSource.ModelData
            elif self.workflow_object.config["build_orthomosaic"]["surface"] == "DenseCloudData":
                self.surface = PhotoScan.DataSource.DenseCloudData
            elif self.workflow_object.config["build_orthomosaic"]["surface"] == "PointCloudData":
                self.surface = PhotoScan.DataSource.PointCloudData
            elif self.workflow_object.config["build_orthomosaic"]["surface"] == "DepthMapsData":
                self.surface = PhotoScan.DataSource.DepthMapsData
            elif self.workflow_object.config["build_orthomosaic"]["surface"] == "TiledModelData":
                self.surface = PhotoScan.DataSource.TiledModelData
            elif self.workflow_object.config["build_orthomosaic"]["surface"] == "OrthomosaicData":
                self.surface = PhotoScan.DataSource.OrthomosaicData
            elif self.workflow_object.config["build_orthomosaic"]["surface"] == "ElevationData":
                self.surface = PhotoScan.DataSource.ElevationData

            if self.workflow_object.config["build_orthomosaic"]["blending"] == "MosaicBlending":
                self.blending = PhotoScan.BlendingMode.MosaicBlending
            elif self.workflow_object.config["build_orthomosaic"]["blending"] == "AverageBlending":
                self.blending = PhotoScan.BlendingMode.AverageBlending
            elif self.workflow_object.config["build_orthomosaic"]["blending"] == "MinBlending":
                self.blending = PhotoScan.BlendingMode.MinBlending
            elif self.workflow_object.config["build_orthomosaic"]["blending"] == "MaxBlending":
                self.blending = PhotoScan.BlendingMode.MaxBlending
            elif self.workflow_object.config["build_orthomosaic"]["blending"] == "DisabledBlending":
                self.blending = PhotoScan.BlendingMode.DisabledBlending

            self.color_correction = self.workflow_object.config["build_orthomosaic"]["color_correction"]
            self.fill_holes = self.workflow_object.config["build_orthomosaic"]["fill_holes"]

        logging.info("Current active chunk is "+self.workflow_object.doc.chunk.label)
        self.workflow_object.doc.chunk.buildOrthomosaic(self.surface,
                                                        self.blending,
                                                        self.color_correction,
                                                        self.fill_holes,
                                                        progress=show_progress)
        logging.info(" Build OrthoMosaic - Finished  " + str(current_utc_datetime()))

    def export(self):
        # set merge chunk as current chunk if split chunk is executed

        # TODO: add option to change projection system for the exported file.
        logging.info("Current active chunk is " + self.workflow_object.doc.chunk.label)
        self.workflow_object.doc.chunk.exportOrthomosaic(self.workflow_object.doc_ortho, format=PhotoScan.RasterFormatTiles,
                                                     image_format=PhotoScan.ImageFormatTIFF,
                                                     raster_transform=PhotoScan.RasterTransformNone, write_kml=False,
                                                     write_world=False, write_alpha=True,
                                                     tiff_compression=PhotoScan.TiffCompressionNone, tiff_big=False,
                                                     jpeg_quality=90)
        logging.debug("Exporting results")
        step = {'params': {}}
        step['params']['surface'] = str(self.surface)
        step['params']['blending'] = str(self.blending)
        step['params']['color_correction'] = str(self.color_correction)
        step['params']['fill_holes'] = str(self.fill_holes)
        step['exports'] = {}
        step['exports']['Orthomosaic'] = str(self.workflow_object.doc_ortho)
        self.export_step_state_details("BuildOrthomosaic", step)