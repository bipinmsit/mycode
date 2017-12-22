import PhotoScan
import logging
import json
import urllib.request as request
import os
import time

from vimana.photoscan_automation.photogrammetry_workflow import *
from datetime import datetime
import json

DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
LAST_PROGRESS_REPORT_TIME = None

def datetime_handler(x):
    if isinstance(x, datetime):
        return x.strftime(DATE_TIME_FORMAT)
    raise TypeError("Unknown type")

def next_step_decision(next_step):
    return lambda x: next_step


def show_progress(percent, **args):
    now = time.time()
    report = False
    global LAST_PROGRESS_REPORT_TIME
    if LAST_PROGRESS_REPORT_TIME == None:
        report = True
        LAST_PROGRESS_REPORT_TIME = now
    else:
        delta = now - LAST_PROGRESS_REPORT_TIME
        print(delta)
        if delta < 5.0:
            report = False
        else:
            report = True
            LAST_PROGRESS_REPORT_TIME = now
    if report:
        print("Percentage completed: ", percent, args)
        logging.warning("Percentage completed: {percent}".format(percent=percent))
        # send post request
        reporting_url = os.environ['PROGRESS_REPORT_URL']
        workflow_id = os.environ['PROGRESS_REPORT_WORKFLOW_ID']
        task_id = os.environ['PROGRESS_REPORT_TASK_ID']
        data = {
            'id': workflow_id,
            'steps': [
                {
                    'name': task_id,
                    'progress': percent
                }
            ]
        }
        req = request.Request(reporting_url,
                              data=json.dumps(data).encode('utf8'),
                              headers={'content-type': 'application/json'})
        try:
            request.urlopen(req)
        except:
            logging.error("could not send request for logging progress")


def calc_total_accuracy(chunk):
    """
    Function to calculate total error of markers
    Args:
        chunk: The chunk for which to calculate total error
    Returns:
        e_sum: Total Error of all the chunks present in 
    Refer:
        http://www.agisoft.com/forum/index.php?topic=4901.0
    """
    e_sum = 0.0
    m_len = len(chunk.markers)
    if m_len == 0:
        # Handling case when there are no markers
        logging.debug("")
        return 10000

    for marker in chunk.markers:
      source = marker.reference.location
      estim = chunk.crs.project(chunk.transform.matrix.mulp(marker.position))
      error = estim - source
      total = error.norm()
      e_sum += total **2
      logging.info("Marker - {ml} Error: {err}".format(ml=marker.label, err= total))
    total_marker_err = float((e_sum/m_len) ** 0.5)
    logging.info("Total Error: {tme}".format(tme=total_marker_err))
    return total_marker_err

def manual_step(step_name):
    print(
        step_name + "is the manual step. Please open PhotoScan in GUI, load project .psx file and complete the step "
                    "manually.")
    print("Remember to save the project after " + step_name)
    prompt_to_run = input("Is the step complete (y/n) ?")
    if prompt_to_run == "y":
        return
    else:
        print("Invalid input!")
        manual_step(step_name)


class PhotogrammetryStep:
    """
    This is an abstract class which defines the methods of a
    photogrammetry step

    """

    def __init__(self, workflow_object):
        self.workflow_object = workflow_object
        self.start_time = current_utc_datetime()
        self.end_time = ""
        self.step_state = {}
        self.is_manual_step = False
        self.state_log_file = os.path.join(os.getcwd() , "current-step-state.json")

    def log_step(self):
        """
        Function to log status of each step in state file.

        """
        if not bool(self.step_state):
            self.step_state = {
                "start_time": self.start_time,
                "status": "processing"
            }

        # logging.info("Step State: " + str(self.step_state))
        data = {
            "steps":[self.step_state]
        }
        # logging.info("Logging Data Initiated:" + str(data))
        try:
            # to avoid conflicting class names from Java proc
            # TODO: refactor the following to remove the Logging call once Java Proc is up
            data["steps"][0].pop('name', None)
            data["steps"][0].pop('next_step', None)
            data.update(data["steps"][0])
            data.pop("steps", None)
            data.pop("id", None)

            ws = open(self.state_log_file, 'w')
            ws.write(json.dumps(data, default=datetime_handler))
            ws.write('\n')
            ws.close()
            # logging.info("Logging Data Successful!")
        except Exception as e:
            # logging.error("Error while logging workflow step:" + str(e))
            pass

    def check_prerequisites(self):
        pass

    def read_params(self):
        pass

    def open_project(self):
        if os.path.isfile(self.workflow_object.doc_name):
            self.open_project_util()
        else:
            self.workflow_object.doc = PhotoScan.app.document
            self.workflow_object.doc.chunk = self.workflow_object.doc.addChunk()
            self.workflow_object.doc.save(self.workflow_object.doc_name)

    def open_project_util(self, project_type='psx'):
        """
        Utility to open project from a .psx or .psz file at the beginning of every step.
        Note: PSX is the default preferred format.
              There are some limitations with the PSZ format. It does not allow you to save DEMs or OrthoMosaics.
        Args:
            project_type: One of ['psx', 'psz']. Controls which format of file will be opened.

        """
        if self.workflow_object:
            if project_type == 'psz':
                logging.info("PSZ: Opening project " + self.workflow_object.doc_name)
                self.workflow_object.doc = PhotoScan.app.document
                self.workflow_object.doc.open(self.workflow_object.doc_name)
            else:
                logging.info("PSX: Opening project " + self.workflow_object.doc_name_psx)
                self.workflow_object.doc = PhotoScan.app.document
                self.workflow_object.doc.open(self.workflow_object.doc_name_psx)

    def set_current_chunk(self, chunk_name):
        """
        Function to set the active chunk, based on chunk_name
        Args:
            chunk_name: Name of the chunk to be set as the active chunk
        """
        chunk_found = False
        for i in range(0, len(self.workflow_object.doc.chunks)):
            individual_chunk = self.workflow_object.doc.chunks[i]
            if str(individual_chunk.label) == str(chunk_name):
                chunk_found = True
                self.workflow_object.doc.chunk = individual_chunk
                logging.info("Current chunk is " + individual_chunk.label)

        if not chunk_found:
            raise ValueError('Chunk name specified not found')

    def execute(self):
        PhotoScan.app.gpu_mask = 3

    def calculate_accuracy(self):
        pass

    def check_accuracy(self):
        pass

    def export(self):
        pass

    def export_step_state_details(self,step_name,step_params = {}):
        """
        Function to save step details in the workflow-state-<project_name>.json file
        Args:
            step_name: Name of the step
            step_params: Extra parameters of the step to be saved. If nothing is specified only start_time,
                         and end_time will be saved.

        """
        fwState = FileWorkflowState(self.workflow_object.workflow_state_file, self.workflow_object.workflow_config_file)
        step_intro = {'name': step_name, 'start_time': self.start_time, 'end_time': current_utc_datetime(), 'status': "completed"}
        self.step_state = step_intro.copy()
        self.step_state.update(step_params)
        fwState.complete_step(self.step_state)
        logging.info('Last Successful Step' + str(fwState.get_last_successful()))
        fwState.save_workflow_state()

    def save_project(self):
        """
        Function to save project as both PSX and PSZ files.

        """
        logging.debug("Saving project " + self.workflow_object.doc_name_psx)
        try:
            # PhotoScan.app.update()
            self.workflow_object.doc.save(self.workflow_object.doc_name_psx)
            self.workflow_object.doc.save()
            self.workflow_object.doc = None
        except RuntimeError:
            logging.error("ERROR: Failed to save project: " + self.workflow_object.doc_name_psx)
            return False
        return True

    def __str__(self):
        return self.__class__.__name__


