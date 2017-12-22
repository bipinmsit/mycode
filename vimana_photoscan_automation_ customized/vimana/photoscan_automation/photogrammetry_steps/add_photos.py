import logging
import os.path
import sys

from vimana.photoscan_automation.photogrammetry_steps.base_steps import PhotogrammetryStep, show_progress, PhotoScan
from vimana.photoscan_automation.photogrammetry_workflow import current_utc_datetime


class AddPhotos(PhotogrammetryStep):
    """
    Add photos step
    """

    def __init__(self, workflow_object):
        super().__init__(workflow_object)
        self.layout = PhotoScan.FlatLayout
        self.start_time = current_utc_datetime()

    def check_prerequisites(self):
        logging.debug("Checking prerequisite")

    def read_params(self):
        logging.debug("Reading params")

        # AddPhotos.execute(self)

    def execute(self):
        logging.info("Started...Add Photos " + str(current_utc_datetime()))

        if "add_photos" in self.workflow_object.config:
            if self.workflow_object.config["add_photos"].get("layout") == "FlatLayout":
                self.layout = PhotoScan.FlatLayout
            elif self.workflow_object.config["add_photos"].get("layout") == "MultiFrameLayout":
                self.layout = PhotoScan.MultiFrameLayout
            elif self.workflow_object.config["add_photos"].get("layout") == "MultiPlaneLayout":
                self.layout = PhotoScan.MultiPlaneLayout

        try:
            images = [os.path.join(self.workflow_object.workflow_images, p) for p in
                      os.listdir(self.workflow_object.workflow_images)]
            logging.debug("Images used are " + str(images))
            self.workflow_object.doc.chunk.addPhotos(images, self.layout, show_progress)
        except RuntimeError as err:
            logging.info("Runtime Error: " + format(err))
            logging.debug("Please add the images to the Images folder and run the script again.")
            sys.exit(1)

        if os.path.exists(self.workflow_object.reference_file):
            logging.info("reference file exist!")
            self.workflow_object.doc.chunk.loadReference(self.workflow_object.reference_file,
                                                     format=PhotoScan.ReferenceFormatCSV, delimiter=',')

        PhotoScan.app.update()
        logging.info("Finished - Adding Photos" + str(current_utc_datetime()))

    def calculate_accuracy(self):
        logging.debug("Calculating the accuracy")
        pass

    def check_accuracy(self):
        logging.debug("Checking accuracy")
        pass

    def export(self):
        logging.debug("Exporting results")
        self.export_step_state_details("AddPhotos")
