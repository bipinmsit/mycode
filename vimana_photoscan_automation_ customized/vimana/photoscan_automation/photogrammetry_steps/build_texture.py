import logging

from vimana.photoscan_automation.photogrammetry_steps.base_steps import PhotogrammetryStep, PhotoScan
from vimana.photoscan_automation.photogrammetry_workflow import current_utc_datetime


class BuildTexture(PhotogrammetryStep):
    """
    we'll build Texture here
    """

    def __init__(self, workflow_object):
        super().__init__(workflow_object)
        self.size = 8192
        self.blending = PhotoScan.MosaicBlending
        self.mapping = PhotoScan.GenericMapping
        self.fill_holes = True
        self.color_correction = False
        self.count = 1
        self.start_time = current_utc_datetime()

    def check_prerequisites(self):
        logging.debug("Checking prerequisite")

    def read_params(self):
        logging.debug("Reading params")

    def execute(self):
        logging.info(" Build Texture - Started  " + str(current_utc_datetime()))
        # set merge chunk as current chunk if split chunk is executed
        if self.workflow_object.split_into_chunk:
            self.set_current_chunk("Merged Chunk")

        if "build_texture" in self.workflow_object.config:
            if self.workflow_object.config["build_texture"]["mapping"] == "GenericMapping":
                self.mapping = PhotoScan.GenericMapping
            elif self.workflow_object.config["build_texture"]["mapping"] == "OrthophotoMapping":
                self.mapping = PhotoScan.OrthophotoMapping
            elif self.workflow_object.config["build_texture"]["mapping"] == "AdaptiveOrthophotoMapping":
                self.mapping = PhotoScan.AdaptiveOrthophotoMapping
            elif self.workflow_object.config["build_texture"]["mapping"] == "CameraMapping":
                self.mapping = PhotoScan.CameraMapping
            elif self.workflow_object.config["build_texture"]["mapping"] == "CurrentMapping":
                self.mapping = PhotoScan.CurrentMapping
            elif self.workflow_object.config["build_texture"]["mapping"] == "SphericalMapping":
                self.mapping = PhotoScan.SphericalMapping

            if self.workflow_object.config["build_texture"]["blending"] == "MosaicBlending":
                self.blending = PhotoScan.MosaicBlending
            elif self.workflow_object.config["build_texture"]["blending"] == "AverageBlending":
                self.blending = PhotoScan.AverageBlending
            elif self.workflow_object.config["build_texture"]["blending"] == "MaxBlending":
                self.blending = PhotoScan.MaxBlending
            elif self.workflow_object.config["build_texture"]["blending"] == "MinBlending":
                self.blending = PhotoScan.MinBlending
            elif self.workflow_object.config["build_texture"]["blending"] == "DisabledBlending":
                self.blending = PhotoScan.DisabledBlending

            self.count = self.workflow_object.config["build_texture"]["texture_count"]
            self.size = self.workflow_object.config["build_texture"]["texture_size"]
            self.color_correction = self.workflow_object.config["build_texture"]["color_correction"]
            self.fill_holes = self.workflow_object.config["build_texture"]["fill_holes"]

        self.workflow_object.doc.chunk.buildUV(self.mapping, self.count)
        self.workflow_object.doc.chunk.buildTexture(self.blending, self.color_correction, self.size, self.fill_holes)
        logging.info(" Build Texture - Finished  " + str(current_utc_datetime()))

    def export(self):
        logging.debug("Exporting results")
        step = {'params': {}}
        step['params']['buildUV'] = {}
        step['params']['build_texture'] = {}
        step['params']['buildUV']['mapping'] = str(self.mapping)
        step['params']['build_texture']['blending'] = str(self.blending)
        step['params']['build_texture']['size'] = str(self.size)
        step['params']['buildUV']['count'] = str(self.count)
        step['params']['build_texture']['color_correction'] = self.color_correction
        step['params']['build_texture']['fill_holes'] = self.fill_holes
        step['exports'] = {}
        step['exports']['model'] = str(self.workflow_object.doc_model)
        self.export_step_state_details("BuildTexture", step)