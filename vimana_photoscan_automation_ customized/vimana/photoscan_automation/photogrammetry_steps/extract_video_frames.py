import logging
import os

from vimana.photoscan_automation.photogrammetry_steps.base_steps import PhotogrammetryStep, PhotoScan
from vimana.photoscan_automation.photogrammetry_workflow import current_utc_datetime
from vimana.photoscan_automation.vidframes import process_videos

class ExtractVideoFrames(PhotogrammetryStep):
    """
    Function to extract Frames from an input video
    """

    def __init__(self, workflow_object):
        super().__init__(workflow_object)
        pass

    def check_prerequisites(self):
        logging.debug("Checking prerequisite")

    def read_params(self):
        logging.debug("Reading params")

    def open_project(self):
        self.open_project_util(project_type='psx')

    def execute(self):
        logging.info(" Frame Extraction from Video Frames - Started  " + str(current_utc_datetime()))
        if os.path.isdir(self.workflow_object.workflow_videos):
            logging.info("Video Directory Found at {}".format(self.workflow_object.workflow_videos))
            try:
                process_videos(self.workflow_object.workflow_videos)
            except Exception as excpt:
                raise RuntimeError("An error occurred while doing video frame extraction. {}".format(str(excpt)))
        else:
            logging.error("Video Directory Not Found!"
                          " Expected video directory at {}".format(self.workflow_object.workflow_videos))


        #TODO: Fill in code to extact frames from video. Use ../vidframes.py
        pass
        logging.info(" Build Tiled Model- Finished  " + str(current_utc_datetime()))

    def export(self):
        logging.debug("Exporting results")
        self.export_step_state_details("ExtractVideoFrames")