import logging

from vimana.photoscan_automation.photogrammetry_steps.base_steps import PhotogrammetryStep, PhotoScan
from vimana.photoscan_automation.photogrammetry_workflow import current_utc_datetime

SUPPORTED_DENSE_CLOUD_FORMATS = ["PointsFormatOBJ", "PointsFormatPLY", "PointsFormatXYZ",
                                 "PointsFormatLAS", "PointsFormatExpe", "PointsFormatU3D",
                                 "PointsFormatPDF", "PointsFormatE57", "PointsFormatOC3",
                                 "PointsFormatPotree", "PointsFormatLAZ", "PointsFormatCL3",
                                 "PointsFormatPTS", "PointsFormatDXF"]

class MergeChunks(PhotogrammetryStep):
    """
    we'll merge chunks
    """

    def check_prerequisites(self):
        logging.debug("Checking prerequisite")
        self.start_time = current_utc_datetime()

    def read_params(self):
        logging.debug("Reading params")

    def execute(self):
        logging.info(" MergeChunks - Started  " + str(current_utc_datetime()))
        chunk_list_to_merge = []
        for i in range(1, len(self.workflow_object.doc.chunks)):
            chunk = self.workflow_object.doc.chunks[i]
            chunk_list_to_merge.append(chunk)
        self.workflow_object.doc.chunks[0].model = None  # removing model from original chunk, just for case
        self.workflow_object.doc.mergeChunks(chunk_list_to_merge, merge_dense_clouds=True,
                                             merge_models=False,
                                             merge_markers=True)  # merging all smaller chunks into single one

        self.set_current_chunk("Merged Chunk")

        # This is due to uncertainty whether CRS is assigned to Merged Chunk
        # and the the fact that there is no project level CRS. All CRS are chunk level.

        self.workflow_object.doc.chunk.marker_location_accuracy = (0.0001, 0.0001, 0.0001)
        self.workflow_object.doc.chunk.marker_projection_accuracy = 0.0001
        self.workflow_object.doc.chunk.updateTransform()

        logging.info(" MergeChunks - Finished  " + str(current_utc_datetime()))

    def export(self):
        """
        We'll export the merged chunks here
        """
        logging.debug("Exporting results")
        export_dense_cloud_params = self.workflow_object.config.get('export_dense_cloud', None)
        export_formats = None
        if export_dense_cloud_params is not None:
            export_formats = export_dense_cloud_params.get("export_formats", None)

        if export_formats is not None:
            for exp_format in export_formats:
                if exp_format in SUPPORTED_DENSE_CLOUD_FORMATS:
                    self.export_dense_cloud(export_dense_cloud_params, exp_format)

        self.export_step_state_details("MergeChunks")

    def export_dense_cloud(self, export_dense_cloud_params, export_format):
        logging.info("Exporting Dense Cloud..")
        active_chunk = self.workflow_object.doc.chunk
        dense_cloud_data = PhotoScan.DataSource.DenseCloudData
        # Setting up dense cloud export parameters
        normals_flag = export_dense_cloud_params.get('normals', True)
        colors_flag = export_dense_cloud_params.get('colors', True)
        binary_flag = export_dense_cloud_params.get('binary_export', True)
        precision = int(export_dense_cloud_params.get('precision', 6))

        if export_format in SUPPORTED_DENSE_CLOUD_FORMATS:
            dense_cloud_format = eval("PhotoScan.PointsFormat." + export_format)
            dense_cloud_ext = export_format.replace("PointsFormat","")
            dense_cloud_ext = dense_cloud_ext.lower()
            output_dense_cloud_path = self.workflow_object.doc_dense_cloud.replace('.cloud', "." + dense_cloud_ext)
            # Exporting Dense Cloud
            logging.info("Exporting Dense Cloud format : {}".format(dense_cloud_format))
            # TODO: Verify if parameters used are appropriate!
            active_chunk.exportPoints(path=output_dense_cloud_path, normals=normals_flag,
                                      format=dense_cloud_format, colors=colors_flag,
                                      precision=precision, source=dense_cloud_data, binary=binary_flag)
            logging.info("Dense Cloud Exported to {}".format(output_dense_cloud_path))
        else:
            logging.error("Specified Dense Cloud format - '{}' not supported by PhotoScan!".format(export_format))