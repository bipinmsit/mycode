import logging

from vimana.photoscan_automation.photogrammetry_steps.base_steps import PhotogrammetryStep, show_progress, PhotoScan
from vimana.photoscan_automation.photogrammetry_workflow import current_utc_datetime


class DetectMarkers(PhotogrammetryStep):
    """
    we'll detect markers here
    """

    def __init__(self, workflow_object):
        super().__init__(workflow_object)
        self.noparity = False
        self.inverted = False
        self.tolerance = 100
        self.type = PhotoScan.CircularTarget12bit
        self.start_time = current_utc_datetime()

    def check_prerequisites(self):
        logging.debug("Checking prerequisite")

    def read_params(self):
        logging.debug("Reading params")

    def execute(self):
        logging.info("Detect Markers - Started" + str(current_utc_datetime()))
        PhotoScan.app.gpu_mask = 3  # GPU devices binary mask

        if "detect_markers" in self.workflow_object.config:
            if self.workflow_object.config["detect_markers"]["type"] == "CircularTarget12bit":
                self.type = PhotoScan.CircularTarget12bit
            elif self.workflow_object.config["detect_markers"]["type"] == "CircularTarget14bit":
                self.type = PhotoScan.CircularTarget14bit
            elif self.workflow_object.config["detect_markers"]["type"] == "CircularTarget16bit":
                self.type = PhotoScan.CircularTarget16bit
            elif self.workflow_object.config["detect_markers"]["type"] == "CircularTarget20bit":
                self.type = PhotoScan.CircularTarget20bit
            elif self.workflow_object.config["detect_markers"]["type"] == "CircularTarget":
                self.type = PhotoScan.CircularTarget
            elif self.workflow_object.config["detect_markers"]["type"] == "CrossTarget":
                self.type = PhotoScan.CrossTarget

            self.tolerance = self.workflow_object.config["detect_markers"]["tolerance"]
            self.inverted = self.workflow_object.config["detect_markers"]["inverted"]
            self.noparity = self.workflow_object.config["detect_markers"]["noparity"]

        self.workflow_object.doc.chunk.detectMarkers(self.type, self.tolerance, self.inverted, self.noparity, show_progress)

        logging.info(" Finished - Detect Markers - Cloud  " + str(current_utc_datetime()))

    def export(self):
        """
        Exports markers
        """
        # Check if marker list is empty or not before exporting the markers
        if self.workflow_object.doc.chunk.markers:
            self.workflow_object.doc.chunk.exportMarkers(self.workflow_object.doc_marker)
        logging.debug("Exporting results")
        step = {'params': {}}
        step['params']['type'] = str(self.type)
        step['params']['tolerance'] = str(self.tolerance)
        step['params']['inverted'] = self.inverted
        step['params']['noparity'] = self.noparity
        step['exports'] = {}
        step['exports']['markers'] = str(self.workflow_object.doc_marker)
        self.export_step_state_details("DetectMarkers",step)