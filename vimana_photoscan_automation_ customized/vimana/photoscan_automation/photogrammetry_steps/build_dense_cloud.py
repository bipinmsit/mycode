import logging

from vimana.photoscan_automation.photogrammetry_steps.base_steps import show_progress, PhotogrammetryStep, PhotoScan
from vimana.photoscan_automation.photogrammetry_workflow import current_utc_datetime

PHOTOSCAN_QUALITY = ["LowestQuality", "LowQuality", "MediumQuality", "HighQuality", "UltraQuality"]
FILTERING = ["AggressiveFiltering", "ModerateFiltering", "MildFiltering", "NoFiltering"]

class BuildDenseCloud(PhotogrammetryStep):
    """
    we'll build dense cloud here
    """

    def __init__(self, workflow_object):
        super().__init__(workflow_object)
        self.filter = PhotoScan.FilterMode.AggressiveFiltering
        self.quality = PhotoScan.Quality.LowestQuality
        self.reuse_depth = False
        self.keep_depth = False
        PhotoScan.app.gpu_mask = 3  # GPU devices binary mask
        self.start_time = current_utc_datetime()

    def check_prerequisites(self):
        logging.debug("Checking prerequisite")

    def read_params(self):
        logging.debug("Reading params")

    def execute(self):
        logging.info("Build Dense Cloud - Started" + str(current_utc_datetime()))

        if "build_dense_cloud" in self.workflow_object.config:
            PhotoScan.app.gpu_mask = self.workflow_object.config["build_dense_cloud"]["gpu_mask"]
            # Assigning Dense Cloud Quality
            if self.workflow_object.config["build_dense_cloud"]["quality"] in PHOTOSCAN_QUALITY:
                dense_cloud_quality = self.workflow_object.config["build_dense_cloud"]["quality"]
                logging.info("Dense Cloud Quality is {}".format(dense_cloud_quality))
                self.quality = eval("PhotoScan.Quality.{}".format(dense_cloud_quality))
            # Assigning Dense Cloud Filtering
            if self.workflow_object.config["build_dense_cloud"]["filter"] in FILTERING:
               dense_cloud_filter = self.workflow_object.config["build_dense_cloud"]["filter"]
               logging.info("Depthi filtering used for Dense Cloud is {}".format(dense_cloud_filter))
               self.filter = eval("PhotoScan.FilterMode.{}".format(dense_cloud_filter))

            self.keep_depth = self.workflow_object.config["build_dense_cloud"]["keep_depth"]
            self.reuse_depth = self.workflow_object.config["build_dense_cloud"]["reuse_depth"]

        if self.workflow_object.split_into_chunk:
            for i in range(1, len(self.workflow_object.doc.chunks)):
                new_chunk = self.workflow_object.doc.chunks[i]
                try:
                    logging.info("Building Dense Cloud for " + new_chunk.label)
                    new_chunk.buildDenseCloud(self.quality, self.filter)
                except RuntimeError:
                    logging.error("Can't build dense cloud for " + new_chunk.label)

        else:
            self.workflow_object.doc.chunk.buildDenseCloud(self.quality, self.filter, progress=show_progress)

        logging.info(" Finished - Build Dense Cloud  " + str(current_utc_datetime()))

    def export(self):
        """
        Exports point cloud.
        """
        if not self.workflow_object.split_into_chunk:
            self.workflow_object.doc.chunk.exportPoints(self.workflow_object.doc_point, source=PhotoScan.DenseCloudData,
                                                    binary=True, precision=6, normals=True, colors=True)

        logging.debug("Exporting results")
        step = {'params': {}}
        step['params']['quality'] = str(self.quality)
        step['params']['filter'] = str(self.filter)
        step['params']['keep_depth'] = str(self.quality)
        step['params']['reuse_depth'] = str(self.filter)
        step['exports'] = {}
        step['exports']['cloud_points'] = str(self.workflow_object.doc_point)
        self.export_step_state_details("BuildDenseCloud",step)