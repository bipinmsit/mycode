import logging
import sys

from vimana.photoscan_automation.photogrammetry_steps.base_steps import show_progress, PhotogrammetryStep, PhotoScan
from vimana.photoscan_automation.photogrammetry_workflow import current_utc_datetime


class GenerateReport(PhotogrammetryStep):
    """
    we'll generate the report here
    """

    def check_prerequisites(self):
        logging.debug("Checking prerequisite")
        self.start_time = current_utc_datetime()

    def read_params(self):
        logging.debug("Reading params")

    def open_project(self):
        self.open_project_util(project_type='psx')

    def execute(self):
        logging.info(" Generate Report - Started  " + str(current_utc_datetime()))

        self.workflow_object.doc.chunks[0].exportReport(self.workflow_object.doc_name_pdf,
                                                self.workflow_object.project_name,
                                                "Generated Report " + self.workflow_object.project_name)
        # set merge chunk as current chunk if split chunk is executed and generate report for merged chunk
        if self.workflow_object.split_into_chunk:
            self.set_current_chunk("Merged Chunk")
            logging.info(self.workflow_object.doc.chunk.label)
            try:
                self.workflow_object.doc.chunk.exportReport(self.workflow_object.doc_merged_chunk_pdf,
                                                            self.workflow_object.project_name,
                                                            "Generated Report " + self.workflow_object.project_name,
                                                            progress=show_progress)
            except OSError as err:
                logging.info("OS error: " + format(err))
                logging.debug("Report is not generated. Run the script again. It will generate the report")
                sys.exit(1)
        logging.info(" Generate Report - Finished  " + str(current_utc_datetime()))

    def export(self):
        logging.debug("Exporting results")
        self.export_step_state_details("GenerateReport")