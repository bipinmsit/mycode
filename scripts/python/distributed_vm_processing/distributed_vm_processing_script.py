#!/usr/bin/env python
import sys
import os
sys.path.append(os.getcwd() + '/python')

import yaml
import argparse
import subprocess
import time
from agent_api_client import AgentClient
from logger import Logger
from communication_utils.slack_util import send_message

# in seconds
BOOT_INSTANCE_RETRY_SECONDS = 120
# in seconds
COMMAND_POST_RETRY_SECONDS = 300


def initialize_machine_costs():
    machines = get_machines()
    return machines


def check_instance_logs(vm):
    try:
        # Agent Client Initialization for interaction with VM
        LOGGER.info("Project: {} Checking Logs on Instance...".format(project_name))
        # Delay before fetching Logs
        time.sleep(30)
        base_url = "http://" + str(vm['internal_ip']) + ":" + str(vm['port'])
        agent_api_client = AgentClient(base_url=base_url)
        return agent_api_client.get_log()
    except Exception as e:
        print(str(e))
        LOGGER.error("Project: {} Error checking logs on instance! Error:{}".format(project_name, str(e)))
        return "Could not fetch logs from instance"


def check_instance_status(vm):
    try:
        # Agent Client Initialization for interaction with VM
        LOGGER.info("Project: {} Checking Instance Status...".format(project_name))
        base_url = "http://" + str(vm['internal_ip']) + ":" + str(vm['port'])
        agent_api_client = AgentClient(base_url=base_url)
        return agent_api_client.get_status()
    except Exception as e:
        print(str(e))
        LOGGER.error("Project: {} Error checking VM status! Error:{}".format(project_name, str(e)))
        raise Exception("Error checking VM status!" + str(e))


def current_epoch():
    return int(time.time())


def boot_instance(vm):
    try:
        gcloud_path = get_gcloud_installed_path()
        start_timestamp = current_epoch()
        boot_instance_retry = 0
        instance_current_status = "starting"
        while (current_epoch() - start_timestamp) <= BOOT_INSTANCE_RETRY_SECONDS \
                and instance_current_status.lower() != "running":
            boot_instance_retry += 1
            try:
                # Check Instance Status
                instance_current_status = check_instance_status(vm)
                LOGGER.info("Project: {} Current Instance Status: {}".format(project_name, instance_current_status))
                # Wait 20 secs
                time.sleep(20)
            except Exception as e:
                LOGGER.warn("Project: {} Error checking VM status, hence VM must be down, Error: {}"
                            .format(project_name, str(e)))
                # Wait 20 secs
                time.sleep(20)

        if instance_current_status.lower() != "running":
            # Start Instance
            LOGGER.info("Project: {} Booting VM after retrying for {} sec, Tries Done: {}!"
                        .format(project_name, BOOT_INSTANCE_RETRY_SECONDS, boot_instance_retry))
            LOGGER.info("Project: {} Starting Instance...".format(project_name))
            instance_start_status = subprocess.Popen([gcloud_path, 'compute', 'instances',
                                                      'start', vm['name'], '--zone', vm['zone']]).wait()

            LOGGER.info("Project: {} Instance Start Status: {}".format(project_name, instance_start_status))
            if instance_start_status != 0:
                LOGGER.error("Project: {} Error starting VM, Terminating!".format(project_name))
                raise Exception("Error Starting VM" + str(e))
            else:
                LOGGER.info("Project: {} Instance Started on Boot Trial Number: {}"
                            .format(project_name, boot_instance_retry))
                LOGGER.info("Project: {} Waiting for Initialization of VM...".format(project_name))
                time.sleep(50)
                return 1
        else:
            LOGGER.error("Project: {} A Process is already running on VM, Terminating!".format(project_name))
            raise Exception("A Process is already running on VM")
    except Exception as e:
        LOGGER.error("Project: {} Error Booting Instance! Error: {}".format(project_name, str(e)))
        raise Exception("Error Booting Instance!" + str(e))


def shutdown_instance(vm):
    try:
        gcloud_path = get_gcloud_installed_path()

        # Stop Instance
        LOGGER.info("Project: {} Shutting Down Instance...".format(project_name))
        instance_stop_status = subprocess.Popen([gcloud_path, 'compute', 'instances',
                                                 'stop', vm['name'], '--zone', vm['zone']]).wait()
        LOGGER.info("Project: {} Instance Stop Status: {}".format(project_name, instance_stop_status))
        if instance_stop_status != 0:
            LOGGER.error("Project: {} Error shutting down VM!".format(project_name))
            raise Exception("Error shutting down VM!")
        else:
            LOGGER.info("Project: {} Waiting for Shutdown of VM...".format(project_name))
            time.sleep(50)
        return instance_stop_status
    except Exception as e:
        LOGGER.error("Project: {} VM Shutdown Failure! Error: {}".format(project_name, str(e)))
        raise Exception("VM Shutdown Failure!" + str(e))


def execute_command_on_instance(vm, command, options=[]):
    try:
        LOGGER.info("Project: {} Running Command on Instance...".format(project_name))
        start_timestamp = current_epoch()
        command_exec_retry = 0
        command_exec_status = 0
        while (current_epoch() - start_timestamp) <= COMMAND_POST_RETRY_SECONDS \
                and command_exec_status != 204:
            command_exec_retry += 1

            # Execute Command after Machine is Up
            try:
                # Agent Client Initialization for interaction with VM
                base_url = "http://" + str(vm['internal_ip']) + ":" + str(vm['port'])
                agent_api_client = AgentClient(base_url=base_url)
                api_args = options
                command_exec_status = agent_api_client.execute_task(command=command, args=api_args)
                # Wait 20 secs
                time.sleep(20)

            except Exception as e:
                LOGGER.warn("Project: {} Error Running Command on VM, Attempting Retry! Error: {}"
                            .format(project_name, str(e)))
                # Wait 20 secs
                time.sleep(20)

        if command_exec_status != 204:
            LOGGER.error("Project: {} Command retried for {} sec, Tries Done: {}!"
                         .format(project_name, COMMAND_POST_RETRY_SECONDS, command_exec_retry))

            raise Exception("Command Retries Overflow!")

        else:
            LOGGER.info("Project: {} Command Executed on Exec Trial Number: {}"
                        .format(project_name, command_exec_retry))
            return 1
    except Exception as e:
        LOGGER.error("Project: {} Command Execution Failure! Error: {}".format(project_name, str(e)))
        raise Exception("Command Execution Failure & VM has been shut down!" + str(e))


def get_gcloud_installed_path():
    try:
        gcloud_installation_path = subprocess.check_output(['which', 'gcloud'])
        LOGGER.info("Project: {} gcloud utility found!".format(project_name))
        return gcloud_installation_path.decode("utf-8").strip()
    except Exception as e:
        LOGGER.error("Project: {} gcloud utility not found, Exiting!".format(project_name))
        raise Exception("GCloud Utility Not Found!" + str(e))


def get_parsed_yaml():
    try:
        if yaml_file_name:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            yaml_file_path = dir_path + "/" + yaml_file_name
            with open(yaml_file_path, 'r') as stream:
                try:
                    parsed_yaml = yaml.load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
        else:
            parsed_yaml = {}
        return parsed_yaml
    except Exception as e:
        LOGGER.error("Project: {} Parsing YAML Failure, Exiting! Error: {}".format(project_name, str(e)))
        raise Exception("Parsing YAML Failure!" + str(e))


def get_vm_config(requested_vm_name):
    valid_machine_names = [each_machine['name'] for each_machine in yaml_as_json['machines']]
    if requested_vm_name not in valid_machine_names:
        LOGGER.info("Project: {} UnSupported VM Name Specified".format(project_name))
        sys.exit(0)
    else:
        return next((item for item in yaml_as_json['machines'] if item['name'] == requested_vm_name), "")


def get_machines():
    try:
        parsed_yaml = get_parsed_yaml()
        if parsed_yaml.get('machines'):
            LOGGER.info("Project: {} Loaded Machines from Config...".format(project_name))
        else:
            LOGGER.error("Project: {} No Machines listed in Config, Terminating!".format(project_name))
            raise Exception("No Machines listed in Config!")

        for each_machine in parsed_yaml.get('machines'):
            each_machine["cost"] = each_machine["cpu"] + 10 * each_machine["gpu"]
        return parsed_yaml.get('machines', [])
    except Exception as e:
        LOGGER.error("Project: {} Error Fetching Machines, Exiting! Error: {}".format(project_name, str(e)))
        raise Exception("Fetch Machines Failure!" + str(e))


def get_steps(adhoc_steps=[]):
    try:
        parsed_yaml = get_parsed_yaml()
        steps_supported = parsed_yaml.get('steps')
        if steps_supported:
            LOGGER.info("Project: {} Loaded Supported Steps from Config...".format(project_name))
            processing_steps = steps_supported
        else:
            LOGGER.error("Project: {} No Steps listed in Config, Terminating!".format(project_name))
            raise Exception("No Steps listed in Config!")

        if adhoc_steps:
            processing_steps = [step for step in steps_supported if step['name'] in adhoc_steps]
            # Validate if all requested Adhoc Steps are supported in Config
            if len(processing_steps) != len(adhoc_steps):
                LOGGER.error("Project: {} Invalid Steps Requested, Terminating!".format(project_name))
                raise Exception("Invalid Steps Requested")
        return processing_steps
    except Exception as e:
        LOGGER.error("Project: {} Error Fetching Steps, Exiting! Error: {}".format(project_name, str(e)))
        raise Exception("Fetch Steps Failure!" + str(e))


def select_vm_for_step(step_to_execute, machines_list):
    try:
        filtered_machines = [m for m in machines_list
                             if m["cpu"] >= step_to_execute["cpu"] and m["gpu"] >= step_to_execute["gpu"]]
        filtered_machines = sorted(filtered_machines, key=(lambda x: x["cost"]), reverse=True)
        if len(filtered_machines) > 0:
            selected_vm = filtered_machines.pop()
            LOGGER.info("Project: {} Selected VM: {}".format(project_name, str(selected_vm)))
        else:
            LOGGER.error("Project: {} No Supported VM Available".format(project_name))
            raise Exception("No Supported VM Available!")
        return selected_vm
    except Exception as e:
        LOGGER.error("Project: {} Error Selecting VM! Error: {}".format(project_name, str(e)))
        raise Exception("VM Selection Failure!" + str(e))


def wait_for_step_execution(vm):
    current_instance_status = "running"
    try:
        while current_instance_status == "running":
            current_instance_status = check_instance_status(vm)
            LOGGER.info("Project: {} Instance is still executing the Command...".format(project_name))
            # Wait 2 minutes
            time.sleep(120)
        if current_instance_status == "error":
            LOGGER.error("Project: {} Instance encountered Error executing the Command! Terminating"
                         .format(project_name))
            raise Exception("Instance encountered Error while executing Command")
        elif current_instance_status != "running":
            LOGGER.info("Project: {} Instance is finished executing the Command...".format(project_name))
            return 1
    except Exception as e:
        LOGGER.error("Project: {} Machine Not Responding While Polling! Error: {}".format(project_name, str(e)))
        raise Exception("Error Machine Not Responding While Polling & VM has been shut down!" + str(e))


def build_message(env, project, vm, step_name="", vm_logs="", success=False):
    if success:
        subject = "[{}] Project: {} Successful Workflow!".format(env.upper(), project)
        message = subject + '\n\n' + "Last VM: {}, Last step: {}".format(vm['name'], step_name)
    else:
        subject = "[{}] Project: {} Failed Workflow!".format(env.upper(), project)
        message = subject + '\n\n' + "Last VM: {}, Last step: {}".format(vm['name'], step_name) + '\n\nLogs\n' \
            + "```{}```".format(vm_logs)

    if env.lower() == 'production':
        channel = 'photoscan'
    else:
        channel = 'photoscan-dev'

    return subject, message, channel


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Arguments for Distributed "
                                                 "VM allocation against resources & processing")
    parser.add_argument("-e", "--environment", help="Environment (development/test/production)", default="development")
    parser.add_argument("-p", "--project_path", help="Local or GCloud Project Path", required=True)
    parser.add_argument("-s", "--steps_list", help="Steps to Run & Override default Series", nargs='+', default=[])
    args = vars(parser.parse_args())

    # Validate Environment
    LOGGER = Logger(environment=args["environment"])

    #####################################
    # VM related variables              #
    #####################################
    last_known_step = ""
    last_known_vm = ""
    vm_logs = ""

    try:
        if args["environment"] == "production":
            yaml_file_name = "distributed_config_production.yaml"
        elif args["environment"] == "test":
            yaml_file_name = "distributed_config_test.yaml"
        elif args["environment"] == "development":
            yaml_file_name = "distributed_config_test.yaml"
        else:
            LOGGER.error("Invalid Environment Specified")
            raise Exception("Invalid Environment Specified!")

        project_path = args["project_path"]
        project_name = project_path.split("/")[-1]
        yaml_as_json = get_parsed_yaml()

        # Get Listed Steps
        custom_steps = args["steps_list"]
        steps_to_execute = get_steps(custom_steps)

        # Get Listed Machines
        machines = initialize_machine_costs()

        for each_step in steps_to_execute:
            last_known_step = each_step['name']
            LOGGER.info("Project: {} Processing Step: {}".format(project_name, each_step['name']))
            # VM Selection
            selected_vm = select_vm_for_step(each_step, machines)
            last_known_vm = selected_vm
            boot_instance(selected_vm)

            try:
                execute_command_on_instance(selected_vm, each_step['name'], options=[project_path])
                wait_for_step_execution(selected_vm)
            except Exception as e:
                vm_logs = check_instance_logs(selected_vm)
                LOGGER.info("Project: {} Shutting Down VM post Command Failure: {}"
                            .format(project_name, selected_vm['name']))
                shutdown_instance(selected_vm)
                raise Exception("Error during Command Execution! " + str(e))

            shutdown_instance(selected_vm)

        LOGGER.info("Project: {} Successful Workflow!".format(project_name))
        subject, message, channel = build_message(
            env=args["environment"],
            project=project_name,
            vm=last_known_vm,
            step_name=last_known_step,
            vm_logs=vm_logs,
            success=True
        )
        send_message(text=message, success=True, channel=channel)
    except Exception as e:
        LOGGER.error("Failed Workflow!, Terminating! Error: {}".format(str(e)))
        subject, message, channel = build_message(
            env=args["environment"],
            project=project_name,
            vm=last_known_vm,
            step_name=last_known_step,
            vm_logs=vm_logs,
            success=False
        )
        send_message(text=message, success=False, channel=channel)
        sys.exit(1)
