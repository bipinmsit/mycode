import uuid
import os.path
import traceback
from decimal import Decimal
from datetime import datetime
import json
import pytz
import socket

from vimana.photoscan_automation.photogrammetry_logger import *
from vimana.photoscan_automation.photogrammetry_graph import *
from vimana.config.config_factory import ConfigFactory

script_path = os.path.realpath(__file__)
vimana_path = os.path.dirname(os.path.dirname(os.path.dirname(script_path)))

sys.path.append(vimana_path)

DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

setup_logging()


def initialize_environment(env="development"):
    logging.info('Environment set: ' + env)
    config = ConfigFactory(env)
    return config.get_environment()


def datetime_handler(x):
    if isinstance(x, datetime):
        return x.strftime(DATE_TIME_FORMAT)
    raise TypeError("Unknown type")


def current_utc_datetime():
    return datetime.utcnow().replace(tzinfo=pytz.utc)


def get_datetime_from_string(s):
    return datetime.strptime(s, DATE_TIME_FORMAT).replace(tzinfo=pytz.utc)


class WorkflowObject:
    """
    Workflow Object that stores config, paths to relevant files and folders, 
    and reference to the PhotoScan Document (PhotoScan.app.document) that is used for all
    processing
    Params:
        (Just the important ones)
        config: Dictionary read from workflow-config.json
        doc: Reference to current PhotoScan.app.document
        split_into_chunk: Boolean. True if processing is happening in multiple chunks.
        id: Workflow UUID
    """

    def __init__(self, skip_manual_steps=True, skip_database_update=True):
        """
        Args:
            skip_manual_steps: Set to True to skip manual steps
            skip_database_update: Set to True to skip database update

        """
        self.split_into_chunk = False
        self.config = None
        self.doc = None
        self.workflow_config_file = None
        self.workflow_state_file = None
        self.id = None
        self.skip_manual_steps = skip_manual_steps
        self.skip_database_update = skip_database_update
        self.VM_name = str(socket.gethostname())
        self.project_name = None


    def initialize_config(self, workflow_config_file):
        """
        Functtion to initialize config based on the workflow-config.json file.
        It will initialize the parameters of the object referred to, by self with values from
        the workflow-config.json file.
        Args:
            self: Reference to object of class WorkflowObject that is calling the function
            workflow_config_file: Path to workflow-config.json file
        Returns:
            int: 0 -> Returns  on successful completion
        """
        self.workflow_config_file = workflow_config_file

        # Reading the Dictionary from the file.
        with open(workflow_config_file, 'r') as input_json:
            self.config = json.load(input_json, parse_int=int, parse_float=Decimal)

        # Checking if the Images are split into chunks while processing.
        if "split_into_chunks" in self.config:
            self.split_into_chunk = True

        # Getting Project Name - Either from workflow-config.json or from name of Project Directory
        initial_setup = self.config.get("initial_setup")
        self.project_name = os.path.basename(os.path.dirname(self.workflow_config_file))

        # Overriding Project Name if it is present in workflow-config.json
        if initial_setup is not None:
            project_name = initial_setup.get("project_name")
            if project_name is not None:
                self.project_name = project_name


        # Initializing Path Variables...
        self.workflow_folder = os.path.join(os.path.dirname(workflow_config_file))
        self.workflow_images = os.path.join(self.workflow_folder, "Images")
        # Adding folder for Video Processing
        self.workflow_videos = os.path.join(self.workflow_folder, "Videos")
        self.workflow_output = os.path.join(self.workflow_folder, "Output")
        self.workflow_workspace = os.path.join(self.workflow_folder, "Photoscan")
        self.workflow_report = os.path.join(self.workflow_folder, "Project Reports", 
                                            "Photoscan Reports")
        self.workflow_input = os.path.join(self.workflow_folder, "Input")
        self.workflow_state_file = os.path.join(self.workflow_workspace,
                                                "workflow-state-" + self.project_name + ".json")

        self.workflow_step_log = os.path.join(self.workflow_folder, "step-result")

        self.doc_name = os.path.join(self.workflow_workspace, self.project_name + ".psz")
        self.doc_name_psx = os.path.join(self.workflow_workspace, self.project_name + ".psx")
        self.doc_name_pdf = os.path.join(self.workflow_report, self.project_name + "-psrep.pdf")
        self.doc_merged_chunk_pdf = os.path.join(self.workflow_report, self.project_name + 
                                                 "merged-psrep.pdf")
        self.doc_camera = os.path.join(self.workflow_workspace, self.project_name + "-camera.xml")
        self.doc_point = os.path.join(self.workflow_workspace, self.project_name + 
                                      "-point-cloud.xyz")
        self.doc_model = os.path.join(self.workflow_workspace, self.project_name + "-model.obj")
        self.doc_dem = os.path.join(self.workflow_output, self.project_name + "-dem.tif")
        self.doc_dense_cloud = os.path.join(self.workflow_output, self.project_name +
                                            "-dense_cloud.cloud")
        self.doc_ortho = os.path.join(self.workflow_output, self.project_name + "-mosaic" + ".tif")
        self.doc_tile = os.path.join(self.workflow_output, self.project_name + "-tile" + ".zip")
        self.doc_matches = os.path.join(self.workflow_workspace, self.project_name + "-matches.txt")
        self.doc_marker = os.path.join(self.workflow_workspace, self.project_name + "-markers.xml")

        # File from which GCP markers will be imported
        self.marker_file = self.workflow_input + "/markers-to-import.csv"
        if os.path.exists(self.marker_file):
            logging.info("markers = " + self.marker_file)

        # TODO: Find out what "reference_file" does
        self.reference_file = self.workflow_input + "/gcp-to-import.csv"
        if os.path.exists(self.reference_file):
            logging.info("reference = " + self.reference_file)
        # Returning 0 on success
        return 0

def create_folder_if_does_not_exist(folder_path, description=""):
    """
    Function to create a folder if it doesn't already exist.
    Args:
        folder_path: Path to the folder to create if it doesn't already exist. 
        description: Description of folder to create when logging. 
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        logging.info(description + " folder not found. The folder has been created at: " + folder_path)


def create_id():
    """
    Function to create UUID
    Returns:
        uuid: uuid as str()
    """
    return str(uuid.uuid4())


class PhotogrammetryWorkflow:
    """
    Represents a photogrammetry workflow.
    """

    def __init__(self, workflow_config_file):
        self.workflow_config_file = os.path.abspath(workflow_config_file)
        # In Local Execution:
        # skip_manual_steps=True
        # skip_database_update=False
        self.workflow_object = WorkflowObject(skip_manual_steps=True, skip_database_update=True)
        self.workflow_object.initialize_config(self.workflow_config_file)
        self.workflow_state = None

        if not os.path.isfile(self.workflow_config_file):
            logging.error("Workflow configuration document does not exist.")
            # raise FileNotFoundError(self.workflow_config_file)

        if os.path.exists(self.workflow_object.workflow_images):
            logging.info("Image folder found at : " + self.workflow_object.workflow_images)
        else:
            logging.info(
                "Images folder not found. The folder has been created at: " + self.workflow_object.workflow_images)
            os.makedirs(self.workflow_object.workflow_images)
            logging.debug("Please add the images to Images folder created and run this script again.")
            raise FileNotFoundError(self.workflow_object.workflow_images)

        self.create_folder_structure()

        self.load_workflow_state()
        self.load_workflow()

    def create_folder_structure(self):
        create_folder_if_does_not_exist(self.workflow_object.workflow_workspace)
        create_folder_if_does_not_exist(self.workflow_object.workflow_input)
        create_folder_if_does_not_exist(self.workflow_object.workflow_report)
        create_folder_if_does_not_exist(self.workflow_object.workflow_output)
        create_folder_if_does_not_exist(self.workflow_object.workflow_step_log)

    def run(self):
        self.nextStep = self.currentStep
        workflow_log = {"start_time": self.workflow_state.created_time, "done": "NO", "status": "processing"}
        self.log_workflow(workflow_log)
        try:
            while self.nextStep is not None:
                logging.info('Initiating' + self.nextStep.__class__.__name__)
                self.nextStep.log_step()
                self.nextStep.check_prerequisites()
                self.nextStep.read_params()
                self.nextStep.open_project()
                self.nextStep.execute()
                self.nextStep.export()
                saved = self.nextStep.save_project()

                if not saved:
                    raise ValueError("Could not save project!")

                # Fetching Next Step
                toProcessStep = self.decide_next_step()
                self.nextStep.step_state.update({"next_step": toProcessStep.__class__.__name__})
                self.nextStep.log_step()
                self.nextStep = toProcessStep

            workflow_log.update({"end_time": current_utc_datetime(), "done": "YES", "status": "completed"})
            self.log_workflow(workflow_log)
        except KeyboardInterrupt:
            logging.error("Keyboard Interrupt!")
            workflow_log.update({"end_time": current_utc_datetime(), "done": "NO", "status": "failed"})
            self.log_workflow(workflow_log)
        except Exception:
            logging.error(traceback.format_exc())
            workflow_log.update({"end_time": current_utc_datetime(), "done": "NO", "status": "failed"})
            self.log_workflow(workflow_log)

    def load_workflow_state(self):
        self.workflow_state = FileWorkflowState(self.workflow_object.workflow_state_file, self.workflow_config_file)
        self.workflow_object.id = self.workflow_state.workflow_id

        logging.info(
            "Loaded workflow state from file " + self.workflow_object.workflow_state_file + " with id " + self.workflow_object.id)

    def load_workflow(self):
        logging.debug('loading workflow state from a file')

        wf_state = self.check_workflow_state_file(self.workflow_object.workflow_state_file)

        logging.info(wf_state)
        # self.workflow_object.initialize_document(self.workflow_object.project_name,
        #                                          self.check_project_file(self.workflow_object.project_name))
        self.dwg = default_photogrammetry_workflow_graph(self.workflow_object)
        if wf_state is not None:
            self.currentStep = self.dwg.get_next_node_by_name(
                self.last_successful_state_name())
            if str(self.currentStep) == "SplitChunks":
                if not self.workflow_object.split_into_chunk:
                    logging.info('Split chunk Regex not found')
                    self.currentStep = self.dwg.get_next_node_by_name("SplitChunks")

            if str(self.currentStep) == "MergeChunks":
                if not self.workflow_object.split_into_chunk:
                    self.currentStep = self.dwg.get_next_node_by_name("MergeChunks")
        else:
            self.currentStep = self.dwg.start

        self.run()

    def last_successful_state_name(self):
        return self.workflow_state.get_last_successful()['name']

    def check_project_file(self, projectName):
        filename = self.workflow_object.workflow_folder + projectName
        if os.path.isfile(filename):
            return True
        else:
            return False

    def check_workflow_state_file(self, workflow_file):
        if os.path.isfile(workflow_file):
            logging.info('Workflow file found at' + workflow_file)
            return True
        else:
            logging.info('Workflow file not found at ' + workflow_file + '. Will create new one at save().')
            return None

    def log_workflow(self, workflow_log):
        ENV_CONFIG = ConfigFactory().get_environment()

        if ENV_CONFIG.TO_MONITOR_LOGS:
            try:
                data = {
                    "id": self.workflow_object.id
                }
                data.update(workflow_log)
            except Exception as e:
                logging.error("Error while logging workflow:" + str(e))
                pass

    def decide_next_step(self):
        to_process_step = self.dwg.get_next(self.nextStep)
        if str(to_process_step) == "SplitChunks":
            if not self.workflow_object.split_into_chunk:
                logging.info('Split chunk Regex not found')
                to_process_step = self.dwg.get_next(to_process_step)

        if str(to_process_step) == "MergeChunks":
            if not self.workflow_object.split_into_chunk:
                to_process_step = self.dwg.get_next(to_process_step)
        return to_process_step


class FileWorkflowState:
    """
    This class creates the JSON for the start state if it doesn't exist else it gives details
    like step name, path to step output file, accuracy, start timestamp and end timestamp in
    JSON format.
    """

    def __init__(self, workflow_steps_json, input_file):
        self.workflow_file = workflow_steps_json
        self.input_file = input_file
        # workflow state attributes
        self.workflow_id = None
        self.created_time = None
        self.workflow_type = None
        self.workflow_steps = None

        if os.path.isfile(self.workflow_file):
            logging.info('Workflow file found at' + self.workflow_file)
            self.load_workflow_state()
        else:
            logging.info('Workflow file not found at ' + self.workflow_file + '. Will create new one at save().')
            self.new_workflow_state()

    def new_workflow_state(self):
        self.created_time = current_utc_datetime()
        self.workflow_id = create_id()

    def load_workflow_state(self):
        logging.info('Loading workflow state from ' + self.workflow_file)
        wf = open(self.workflow_file, 'r')
        state = json.load(wf)
        logging.debug(state)
        self.workflow_id = state['id']
        self.created_time = get_datetime_from_string(state['created_time'])
        self.workflow_type = state['type']
        self.workflow_steps = []
        for s in state['steps']:
            self.workflow_steps.append(s)

    def save_workflow_state(self):
        logging.info('Saving workflow state at ' + self.workflow_file)

        state_str = json.dumps({
            'id': self.workflow_id,
            'input_file_path': self.input_file,
            'type': 'photogrammetry (photoscan) workflow document v0.1b',
            'workflow_json_file': self.workflow_file,
            'created_time': self.created_time,
            'steps': self.workflow_steps
        }, default=datetime_handler, indent=10)
        wf = open(self.workflow_file, 'w')
        wf.write(state_str)
        wf.write('\n')
        logging.debug(state_str)
        wf.close()

    def get_last_successful(self):
        if self.workflow_steps is not None and len(self.workflow_steps) > 0:
            last_step = self.workflow_steps[len(self.workflow_steps) - 1]
            if isinstance(last_step, list):
                return last_step[0]
            else:
                return last_step
        else:
            return None

    def complete_step(self, step, **kwargs):
        step_id = 1
        last_step = self.get_last_successful()

        if last_step is not None:
            step_id = int(last_step['id']) + 1
        Sid = {}
        Sid['id'] = step_id
        step = create_step(Sid, step)

        if self.workflow_steps is None:
            self.workflow_steps = []

        self.workflow_steps.append(step)

    def __str__(self):
        s = "Workflow\n"
        s += "-- version = " + str(self.workflow_type) + "\n"
        s += "-- created = " + str(self.created_time.strftime(DATE_TIME_FORMAT)) + "\n"
        s += "-- id = " + str(self.workflow_id) + "\n"
        return s


def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z


def create_step(id, step):
    return merge_two_dicts(id, step)


if __name__ == "__main__":
    """
    This is main for workflow controller 
      Arg1(optional): path to workflowConfig.json
      Arg2(optional): <env> e.g: test, production, development
    """
    try:
        logging.debug(sys.argv)
        if len(sys.argv) > 1:
            if len(sys.argv) > 2:
                environment = sys.argv[2]
            else:
                # Setting default environment as development
                environment = "development"
            initialize_environment(environment)
            PhotogrammetryWorkflow(sys.argv[1])
        else:
            initialize_environment("development")
            inp = input("No arguments were given. Do you want to continue without argments (y/n) ? : ")
            if inp == "y":
                # create a input json file path
                input_json_file_path = os.path.join(os.getcwd(), "workflow-config.json")

                if os.path.isfile(input_json_file_path):
                    PhotogrammetryWorkflow(input_json_file_path)
                else:
                    logging.info("Please create the workflow-config.json and run the script")
            else:
                logging.info("Please create the workflow-config.json and run the script")
                sys.exit(1)
    except Exception as err:
        logging.error(err)
        sys.exit(1)
