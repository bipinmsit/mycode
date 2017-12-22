import logging
import os.path

from vimana.photoscan_automation.photogrammetry_steps.base_steps import PhotogrammetryStep, calc_total_accuracy, PhotoScan
from vimana.photoscan_automation.photogrammetry_workflow import current_utc_datetime


class OptimizeCamera(PhotogrammetryStep):
    """
    Optimize camera
    """

    def __init__(self, workflow_object):
        super().__init__(workflow_object)
        self.start_time = current_utc_datetime()

    def check_prerequisites(self):
        logging.debug("Checking prerequisite")

    def read_params(self):
        logging.debug("Reading params")

    def execute(self):
        logging.info("Started- Optimize camera" + str(current_utc_datetime()))

        self.workflow_object.doc.chunk.optimizeCameras(fit_f=True, fit_cx=True, fit_cy=True, fit_b1=True, fit_b2=True,
                                                   fit_k1=True, fit_k2=True, fit_k3=True, fit_k4=True, fit_p1=True,
                                                   fit_p2=True, fit_p3=True, fit_p4=True, fit_shutter=True)

        # Checking if Accuracy requirements are satisfied.
        req_marker_accuracy = float(self.workflow_object.config.get('marker_accuracy', 0.01))
        # Check Error only if marker file was used
        if os.path.exists(self.workflow_object.marker_file):
            actual_marker_accuracy = calc_total_accuracy(self.workflow_object.doc.chunk)
            # Logging
            logging.info("Required Marker Accuracy = {}m".format(req_marker_accuracy))
            logging.info("Actual Marker Accuracy = {}m".format(actual_marker_accuracy))

            if actual_marker_accuracy > req_marker_accuracy:

                # Throw Error
                logging.error("Actual Marker accuracy does not satisfy required marker accuracy! \n"
                            " Exiting with Error!!")
                raise RuntimeError("Marker Error Too high!")

        logging.info("Finished- Optimize camera" + str(current_utc_datetime()))

    def export(self):
        logging.debug("Exporting results")
        self.export_step_state_details("OptimizeCamera")