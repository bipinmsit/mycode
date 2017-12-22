import logging
import os.path

from vimana.photoscan_automation.photogrammetry_steps.base_steps import PhotogrammetryStep, PhotoScan
from vimana.photoscan_automation.photogrammetry_workflow import current_utc_datetime
from vimana.photoscan_automation.import_marker import read_marker

class AddGCPs(PhotogrammetryStep):
    """
    we'll detect markers here
    """

    def check_prerequisites(self):
        logging.debug("Checking prerequisite")
        self.start_time = current_utc_datetime()

    def read_params(self):
        logging.debug("Reading params")

    def execute(self):
        logging.info("AddGCPs - Started" + str(current_utc_datetime()))

        if os.path.exists(self.workflow_object.marker_file):
            logging.info("marker file exist!")
            # uncheck all the camera
            for camera in self.workflow_object.doc.chunk.cameras:
                camera.reference.enabled = False

            read_marker(self.workflow_object.marker_file, self.workflow_object.doc.chunk)

            # Assigning PhotoScan Project Coordinate System as EPSG:9001 - Local Coordinates in metres
            self.workflow_object.doc.chunk.crs = PhotoScan.CoordinateSystem('LOCAL_CS["Local Coordinates",LOCAL_DATUM["Local Datum",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]')

            self.workflow_object.doc.chunk.marker_location_accuracy = (0.0001, 0.0001, 0.0001)
            self.workflow_object.doc.chunk.marker_projection_accuracy = 0.0001

        logging.info(" Finished - Detect Markers - Cloud  " + str(current_utc_datetime()))

    def export(self):
        """
        Exports markers
        """
        # Check if marker list is empty or not before exporting the markers
        logging.debug("Exporting results")
        self.export_step_state_details("AddGCPs")
