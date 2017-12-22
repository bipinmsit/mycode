import logging

from vimana.photoscan_automation.photogrammetry_steps.base_steps import PhotogrammetryStep, show_progress, PhotoScan
from vimana.photoscan_automation.photogrammetry_workflow import current_utc_datetime


class EstimateImageQuality(PhotogrammetryStep):
    """
    estimate image quality
    """

    def __init__(self, workflow_object):
        super().__init__(workflow_object)
        self.threshold = 0.5
        self.start_time = current_utc_datetime()

    def check_prerequisites(self):
        logging.debug("Checking prerequisite")

    def read_params(self):
        logging.debug("Reading params")

    def execute(self):
        logging.info("Started- Estimating Image quality" + str(current_utc_datetime()))

        for camera in self.workflow_object.doc.chunk.cameras:
            self.workflow_object.doc.chunk.estimateImageQuality([camera], show_progress)
            quality = float(camera.photo.meta['Image/Quality'])
            logging.info("Quality for this image is: " + str(quality))
        if "estimate_image_quality" in self.workflow_object.config:
            self.threshold = self.workflow_object.config["estimate_image_quality"]["threshold"]

        if quality < self.threshold:
            camera.enabled = False

        logging.info("Finished- Estimating Image quality" + str(current_utc_datetime()))

    def export(self):
        logging.debug("Exporting results")
        step = {'params': {}}
        step['params']['threshold'] = str(self.threshold)
        self.export_step_state_details("EstimateImageQuality",step)