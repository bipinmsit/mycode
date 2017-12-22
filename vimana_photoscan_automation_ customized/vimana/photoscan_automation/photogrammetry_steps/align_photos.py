import logging

from vimana.photoscan_automation.photogrammetry_steps.base_steps import show_progress, PhotogrammetryStep, PhotoScan
from vimana.photoscan_automation.photogrammetry_workflow import current_utc_datetime

PHOTOSCAN_ACCURACY = ["LowestAccuracy", "LowAccuracy", "MediumAccuracy", "HighAccuracy", "HighestAccuracy"]
PRESELECTION = ["NoPreselection", "GenericPreselection", "ReferencePreselection"]

class AlignPhotos(PhotogrammetryStep):
    """
    align photos
    """

    def __init__(self, workflow_object):
        super().__init__(workflow_object)
        self.fit_shutter = True
        self.fit_p4 = True
        self.fit_p3 = True
        self.fit_p2 = True
        self.fit_p1 = True
        self.fit_k4 = True
        self.fit_k3 = True
        self.fit_k2 = True
        self.fit_k1 = True
        self.fit_b2 = True
        self.fit_b1 = True
        self.fit_cy = True
        self.fit_cx = True
        self.fit_f = True
        self.adaptive_fitting = True
        self.minimum_number_of_point_projection = 1
        self.tiepoint_limit = 500
        self.keypoint_limit = 4000
        self.filter_mask = False
        self.reference_preselection = True
        self.generic_preselection = True
        self.preselection = PhotoScan.ReferencePreselection
        self.accuracy = PhotoScan.Accuracy.MediumAccuracy
        PhotoScan.app.gpu_mask = 3
        self.start_time = current_utc_datetime()

    def check_prerequisites(self):
        logging.debug("Checking prerequisite")

    def read_params(self):
        logging.debug("Reading params")

    def execute(self):
        logging.info("Started...Align Photos" + str(current_utc_datetime()))

        if "align_photos" in self.workflow_object.config:
            PhotoScan.app.gpu_mask = self.workflow_object.config["align_photos"]["gpu_mask"]  # GPU devices binary mask

            if self.workflow_object.config["align_photos"]["accuracy"] in PHOTOSCAN_ACCURACY:
                align_accuracy = self.workflow_object.config["align_photos"]["accuracy"]
                logging.info("Align Photos Accuracy is {}".format(align_accuracy))
                self.accuracy = eval("PhotoScan.Accuracy.{}".format(align_accuracy))

            if self.workflow_object.config["align_photos"]["preselection"] in PRESELECTION:
                align_preselection = self.workflow_object.config["align_photos"]["preselection"]
                logging.info("Align Photos: Preselection used is {}".format(align_preselection))
                self.preselection = eval("PhotoScan.{}".format(align_preselection))


            self.generic_preselection = self.workflow_object.config["align_photos"]["generic_preselection"]
            self.reference_preselection = self.workflow_object.config["align_photos"]["reference_preselection"]

            self.filter_mask = self.workflow_object.config["align_photos"]["filter_mask"]
            self.keypoint_limit = int(self.workflow_object.config["align_photos"]["keypoint_limit"])
            self.tiepoint_limit = int(self.workflow_object.config["align_photos"]["tiepoint_limit"])

            if "align_cameras" in self.workflow_object.config["align_photos"]:
                self.min_img = self.workflow_object.config["align_photos"]["min_image"]
                self.adaptive_fitting = self.workflow_object.config["align_photos"]["adaptive_fitting"]

            if "optimize_cameras" in self.workflow_object.config["align_photos"]:
                self.fit_f = self.workflow_object.config["align_photos"]["optimize_cameras"]["fit_f"]
                self.fit_cx = self.workflow_object.config["align_photos"]["optimize_cameras"]["fit_cx"]
                self.fit_cy = self.workflow_object.config["align_photos"]["optimize_cameras"]["fit_cy"]
                self.fit_b1 = self.workflow_object.config["align_photos"]["optimize_cameras"]["fit_b1"]
                self.fit_b2 = self.workflow_object.config["align_photos"]["optimize_cameras"]["fit_b2"]
                self.fit_k1 = self.workflow_object.config["align_photos"]["optimize_cameras"]["fit_k1"]
                self.fit_k2 = self.workflow_object.config["align_photos"]["optimize_cameras"]["fit_k2"]
                self.fit_k3 = self.workflow_object.config["align_photos"]["optimize_cameras"]["fit_k3"]
                self.fit_k4 = self.workflow_object.config["align_photos"]["optimize_cameras"]["fit_k4"]
                self.fit_p1 = self.workflow_object.config["align_photos"]["optimize_cameras"]["fit_p1"]
                self.fit_p2 = self.workflow_object.config["align_photos"]["optimize_cameras"]["fit_p2"]
                self.fit_p3 = self.workflow_object.config["align_photos"]["optimize_cameras"]["fit_p3"]
                self.fit_p4 = self.workflow_object.config["align_photos"]["optimize_cameras"]["fit_p4"]
                self.fit_shutter = self.workflow_object.config["align_photos"]["optimize_cameras"]["fit_shutter"]

        logging.info("Align Photos - Variable assignment complete!")
        # Assigning Photoscan Project Coordinate System to EPSG::4326
        self.workflow_object.doc.chunk.crs = PhotoScan.CoordinateSystem('EPSG::4326')

        self.workflow_object.doc.chunk.matchPhotos(self.accuracy, self.preselection, self.generic_preselection,
                                                   self.reference_preselection, self.filter_mask, self.keypoint_limit,
                                                   self.tiepoint_limit)

        self.workflow_object.doc.chunk.alignCameras(progress=show_progress)

        # TODO: Replace hardocded parameter values or change config file. Discuss!
        self.workflow_object.doc.chunk.optimizeCameras(fit_f=True, fit_cx=True, fit_cy=True, fit_b1=True, fit_b2=True,
                                                   fit_k1=True, fit_k2=True, fit_k3=True, fit_k4=True, fit_p1=True,
                                                   fit_p2=True, fit_p3=True, fit_p4=True, fit_shutter=True)

        logging.info("Finished - Align Photos" + str(current_utc_datetime()))

    def export(self):
        """
        We will export the matches and/or camera positions.
        """
        self.workflow_object.doc.chunk.exportCameras(path=self.workflow_object.doc_camera)
        self.workflow_object.doc.chunk.exportMatches(path=self.workflow_object.doc_matches)
        logging.debug("Exporting results")
        step = {'params': {}}
        step['params']['accuracy'] = str(self.accuracy)
        step['params']['preselection'] = str(self.preselection)
        step['params']['coordinate_system'] = str(self.workflow_object.doc.chunk.crs)
        step['params']['filter_mask'] = self.filter_mask
        step['params']['keypoint_limit'] = self.keypoint_limit
        step['params']['tiepoint_limit'] = self.tiepoint_limit
        step['exports'] = {}
        step['exports']['exported_camera_path'] = str(self.workflow_object.doc_camera)
        step['exports']['exported_matches_path'] = str(self.workflow_object.doc_matches)
        self.export_step_state_details("AlignPhotos",step)