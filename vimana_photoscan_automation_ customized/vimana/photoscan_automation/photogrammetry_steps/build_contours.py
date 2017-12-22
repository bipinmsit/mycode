import logging

from vimana.photoscan_automation.photogrammetry_steps.base_steps import PhotogrammetryStep, PhotoScan
from vimana.photoscan_automation.photogrammetry_workflow import current_utc_datetime


class BuildContours(PhotogrammetryStep):
    """
    We'll build the Contours here
    """

    def __init__(self, workflow_object):
        super().__init__(workflow_object)
        self.interval = 1
        self.source_data = PhotoScan.DataSource.ModelData
        self.start_time = current_utc_datetime()

    def check_prerequisites(self):
        logging.debug("Checking prerequisite")

    def read_params(self):
        logging.debug("Reading params")

    def execute(self):
        logging.info(" Build Contours - Started  " + str(current_utc_datetime()))
        # set merge chunk as current chunk if split chunk is executed
        if self.workflow_object.split_into_chunk:
            self.set_current_chunk("Merged Chunk")

        if "build_contours" in self.workflow_object.config:
            if self.workflow_object.config["build_contours"]["source_data"] == "elevationdata":
                self.source_data = PhotoScan.ElevationData

            self.interval = self.workflow_object.config["build_contours"]["interval"]

        self.workflow_object.doc.chunk.buildContours(source_data=PhotoScan.ElevationData, interval=1)
        logging.info(" Build Contours - Finished  " + str(current_utc_datetime()))

    def export(self):

        logging.debug("Exporting results")
        step = {'params': {}}
        step['params']['source_data'] = str(self.source_data)
        step['params']['interval'] = str(self.interval)
        self.export_step_state_details("BuildContours", step)