import logging

from vimana.photoscan_automation.photogrammetry_steps.base_steps import PhotogrammetryStep, PhotoScan
from vimana.photoscan_automation.photogrammetry_workflow import current_utc_datetime


class BuildTiledModel(PhotogrammetryStep):
    """
    We'll build the Tiled Model here
    """

    def __init__(self, workflow_object):
        super().__init__(workflow_object)
        self.pixel_size = 0.0045909,
        self.tile_size = 256
        self.start_time = current_utc_datetime()

    def check_prerequisites(self):
        logging.debug("Checking prerequisite")

    def read_params(self):
        logging.debug("Reading params")

    def open_project(self):
        self.open_project_util(project_type='psx')

    def execute(self):
        logging.info(" Build Tiled Model - Started  " + str(current_utc_datetime()))
        # set merge chunk as current chunk if split chunk is executed
        if self.workflow_object.split_into_chunk:
            self.set_current_chunk("Merged Chunk")

        if "build_tiled_model" in self.workflow_object.config:
            self.tile_size = self.workflow_object.config["build_tiled_model"]["tile_size"]

        self.workflow_object.doc.chunk.buildTiledModel(self.pixel_size, self.tile_size, source=PhotoScan.DenseCloudData)
        logging.info(" Build Tiled Model- Finished  " + str(current_utc_datetime()))

    def export(self):
        self.workflow_object.doc.chunk.exportTiledModel(self.workflow_object.doc_tile)
        logging.debug("Exporting results")
        step = {'params': {}}
        step['params']['tile_size'] = str(self.tile_size)
        step['exports'] = {}
        step['exports']['TiledModel'] = str(self.workflow_object.doc_tile)
        self.export_step_state_details("BuildTiledModel", step)