import logging

from vimana.photoscan_automation.photogrammetry_steps.base_steps import PhotogrammetryStep, manual_step, PhotoScan
from vimana.photoscan_automation.photogrammetry_workflow import current_utc_datetime


class BoundingBox(PhotogrammetryStep):
    """
    we'll build Bounding Box here
    """

    def __init__(self, workflow_object):
        super().__init__(workflow_object)
        self.is_manual_step = True

    def check_prerequisites(self):
        logging.debug("Checking prerequisite")
        self.start_time = current_utc_datetime()

    def read_params(self):
        logging.debug("Reading params")

    def execute(self):
        PhotoScan.app.messageBox("BoundingBox is a manual step as of now")
        PhotoScan.app.messageBox("Please open PhotoScan project in GUI, add bounding box and save the file")

    def export(self):
        if self.workflow_object.skip_manual_steps:
            logging.info('Skipping Manual Step: ' + self.__class__.__name__)
            self.step_state.update({"status": "skipped"})
            return
        manual_step("Bounding Box")
        self.export_step_state_details("BoundingBox")