import logging

from vimana.photoscan_automation.photogrammetry_steps.base_steps import PhotogrammetryStep, PhotoScan
from vimana.photoscan_automation.photogrammetry_workflow import current_utc_datetime


class BuildMesh(PhotogrammetryStep):
    """
    we'll build mesh here
    """

    def __init__(self, workflow_object):
        super().__init__(workflow_object)
        self.interpolation = PhotoScan.EnabledInterpolation
        self.face_count = PhotoScan.HighFaceCount
        self.source = PhotoScan.DenseCloudData
        self.surface = PhotoScan.Arbitrary
        self.vertex_colors = True
        self.start_time = current_utc_datetime()

    def check_prerequisites(self):
        logging.debug("Checking prerequisite")

    def read_params(self):
        logging.debug("Reading params")

    def execute(self):
        logging.info(" Build Mesh - Started  " + str(current_utc_datetime()))

        if "build_mesh" in self.workflow_object.config:
            if self.workflow_object.config["build_mesh"]["surface"] == "HeightField":
                self.surface = PhotoScan.HeightField
            elif self.workflow_object.config["build_mesh"]["surface"] == "Arbitrary":
                self.surface = PhotoScan.Arbitrary

            if self.workflow_object.config["build_mesh"]["source"] == "DenseCloudData":
                self.source = PhotoScan.DenseCloudData
            elif self.workflow_object.config["build_mesh"]["source"] == "PointCloudData":
                self.source = PhotoScan.PointCloudData
            elif self.workflow_object.config["build_mesh"]["source"] == "DepthMapsData":
                self.source = PhotoScan.DepthMapsData
            elif self.workflow_object.config["build_mesh"]["source"] == "ModelData":
                self.source = PhotoScan.ModelData
            elif self.workflow_object.config["build_mesh"]["source"] == "TiledModelData":
                self.source = PhotoScan.TiledModelData
            elif self.workflow_object.config["build_mesh"]["source"] == "OrthomosaicData":
                self.source = PhotoScan.OrthomosaicData

            if self.workflow_object.config["build_mesh"]["face_count"] == "HighFaceCount":
                self.face_count = PhotoScan.HighFaceCount
            elif self.workflow_object.config["build_mesh"]["face_count"] == "MediumFaceCount":
                self.face_count = PhotoScan.MediumFaceCount
            elif self.workflow_object.config["build_mesh"]["face_count"] == "LowFaceCount":
                self.face_count = PhotoScan.LowFaceCount
            else:
                self.face_count = self.workflow_object.config["build_mesh"]["face_count"]

            if self.workflow_object.config["build_mesh"]["interpolation"] == "EnabledInterpolation":
                self.interpolation = PhotoScan.EnabledInterpolation
            elif self.workflow_object.config["build_mesh"]["interpolation"] == "ExtrapolatedInterpolation":
                self.interpolation = PhotoScan.ExtrapolatedInterpolation
            elif self.workflow_object.config["build_mesh"]["interpolation"] == "DisabledInterpolation":
                self.interpolation = PhotoScan.DisabledInterpolation

            self.vertex_colors = self.workflow_object.config["build_mesh"]["vertex_colors"]

        if self.workflow_object.split_into_chunk:
            for i in range(1, len(self.workflow_object.doc.chunks)):
                new_chunk = self.workflow_object.doc.chunks[i]
                try:
                    logging.info("Building Mesh for " + new_chunk.label)
                    new_chunk.buildModel(self.surface, self.interpolation, self.face_count, self.source)
                except RuntimeError:
                    logging.error("Can't build dense cloud for " + self.new_chunk.label)

        else:
            self.workflow_object.doc.chunk.buildModel(self.surface, self.interpolation, self.face_count, self.source)

        logging.info(" Build Mesh - Finished  " + str(current_utc_datetime()))

    def export(self):
        """
        We'll export the model here
        """
        if not self.workflow_object.split_into_chunk:
            self.workflow_object.doc.chunk.exportModel(self.workflow_object.doc_model, binary=True, precision=6,
                                                   texture=True,
                                                   normals=True, colors=True, cameras=True)
        logging.debug("Exporting results")
        step = {'params': {}}
        step['params']['surface'] = str(self.surface)
        step['params']['source'] = str(self.source)
        step['params']['face_count'] = str(self.face_count)
        step['params']['interpolation'] = str(self.interpolation)
        step['exports'] = {}
        step['exports']['model'] = str(self.workflow_object.doc_model)
        self.export_step_state_details("BuildMesh", step)