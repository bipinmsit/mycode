import logging

from vimana.photoscan_automation.photogrammetry_steps.base_steps import PhotogrammetryStep, PhotoScan
from vimana.photoscan_automation.photogrammetry_workflow import current_utc_datetime
import re

class SplitChunks(PhotogrammetryStep):
    """
    Split into Chunks
    """

    def check_prerequisites(self):
        logging.debug("Checking prerequisite")
        self.start_time = current_utc_datetime()

    def read_params(self):
        logging.debug("Reading params")

    def create_chunk_list(self, dictionary_of_regex=None):
        chunk_list = []
        for k, v in dictionary_of_regex.items():
            if isinstance(v, dict):
                return self.create_chunk_list(v)
            else:
                a_list = list([k, v])
                chunk_list.append(a_list)
        return chunk_list

    def execute(self):
        logging.info("Started- Split Chunk" + str(current_utc_datetime()))

        if not self.workflow_object.doc.chunk.transform.translation:
            self.workflow_object.doc.chunk.transform.matrix = self.workflow_object.doc.chunk.transform.matrix

        chunk_list = self.create_chunk_list(self.workflow_object.config["split_into_chunks"])
        length_of_chunk_list = len(chunk_list)
        count = 0
        for j in range(1, length_of_chunk_list + 1):  # creating new chunks and removing the camera
            new_chunk = self.workflow_object.doc.chunks[0].copy(items=[PhotoScan.DataSource.DenseCloudData])
            new_chunk.label = str(chunk_list[count][0])
            new_chunk.model = None
            regex_expression = chunk_list[count][1]
            pattern = re.compile(regex_expression)
            count = count + 1
            for camera in list(new_chunk.cameras):
                if not pattern.match(camera.label):
                    new_chunk.remove(camera)
                else:
                    logging.info(new_chunk.label + " has " + camera.label)

            PhotoScan.app.update()

        logging.info("Finished- Split Chunks" + str(current_utc_datetime()))

    def export(self):
        logging.debug("Exporting results")
        self.export_step_state_details("SplitChunks")