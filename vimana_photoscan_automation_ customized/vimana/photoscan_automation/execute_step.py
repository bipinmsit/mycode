#!env python
"""
Entry point script for executing a single step
"""
import os
import sys
import inspect
import argparse

script_path = os.path.realpath(__file__)
vimana_path = os.path.dirname(os.path.dirname(os.path.dirname(script_path)))
sys.path.append(vimana_path)
from vimana.photoscan_automation.photogrammetry_graph import *
import vimana.photoscan_automation.photogrammetry_steps as pg_step

from vimana.photoscan_automation.photogrammetry_workflow import WorkflowObject

STEP_CLASSES = inspect.getmembers(pg_step, inspect.isclass)


def execute_step(step_type, cwd=None):
    if cwd is not None:
        print('Changing CWD to {0}'.format(cwd))
        os.chdir(str(cwd))
    workflow_config = create_workflow_config()
    print('Executing step: {0}'.format(step_type))
    step = create_step(step_type, workflow_config)
    print('Create step object: {0}'.format(step))
    step.log_step()
    step.check_prerequisites()
    step.read_params()
    step.open_project()
    step.execute()
    step.export()
    saved = step.save_project()
    step.log_step()
    if not saved:
        raise ValueError("Could not save project!")


def create_step(step_type, workflow_config):
    classes = [cls for name, cls in STEP_CLASSES if name == step_type]
    if len(classes) == 0:
        return None
    return classes[0](workflow_config)


def create_workflow_config():
    workflow_config_file = os.path.join(os.getcwd(), 'workflow-config.json')
    workflow_object = WorkflowObject(skip_manual_steps=True, skip_database_update=True)
    workflow_object.initialize_config(workflow_config_file)
    return workflow_object


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Execute a single photogrammetry step')
    parser.add_argument('step_type', help='which step to run')
    parser.add_argument('-d', '--dir', help='directory path to change CWD to')
    args = parser.parse_args()
    execute_step(args.step_type, cwd=args.dir)
