import logging

from vimana.photoscan_automation.photogrammetry_steps.base_steps import PhotogrammetryStep, PhotoScan
from vimana.photoscan_automation.photogrammetry_workflow import current_utc_datetime


class CheckMarkerError(PhotogrammetryStep):
    """
    Check for Marker error and remove the marker if error is more than threshold
    """

    def check_prerequisites(self):
        logging.debug("Checking prerequisite")
        self.start_time = current_utc_datetime()

    def read_params(self):
        logging.debug("Reading params")

    def execute(self):
        logging.info("Started- CheckMarkerError " + str(current_utc_datetime()))
        for camera in self.workflow_object.doc.chunk.cameras:
            for marker in self.workflow_object.doc.chunk.markers:
                if not marker.projections[camera]:
                    continue
                else:
                    projections = marker.projections[camera].coord
                    reprojection = camera.project(marker.position)
                    if reprojection is not None:
                        error = (projections - reprojection)

                        if error.norm() > 0.5:
                            print(marker.label, camera.label)
                            marker.projections[camera] = None
                            PhotoScan.app.update()
                            self.execute()

        logging.info("Finished- CheckMarkerError" + str(current_utc_datetime()))

    def export(self):
        logging.debug("Exporting results")
        self.export_step_state_details("CheckMarkerError")