# Usage

Root Folder for execution: scripts folder
This package is for triggering Distributed Workflow for Photogrammatry steps:

```sh
Usage: distributed_vm_processing_script.py [-h] [-e ENVIRONMENT] -p
                                           PROJECT_PATH
                                           [-s STEPS_LIST [STEPS_LIST ...]]

Arguments for Distributed VM allocation against resources & processing

optional arguments:
  -h, --help            show this help message and exit
  -e ENVIRONMENT, --environment ENVIRONMENT
                        Environment (development/test/production)
  -p PROJECT_PATH, --project_path PROJECT_PATH
                        Local or GCloud Project Path
  -s STEPS_LIST [STEPS_LIST ...], --steps_list STEPS_LIST [STEPS_LIST ...]
                        Steps to Run & Override default Series
```

Example Usage:
* To run all steps against a project:
  ```sh
  python distributed_vm_processing_script.py -e test -p gs:/path-to-project  
  ```

* To run specific steps against a project (This will run the requested steps in order of config mentioned in yaml file):
  ```sh
  python distributed_vm_processing_script.py -e test -p gs:/path-to-project -s add_photos align_photos  
  ```
  
  ***Note: Default environment is: development***
  
# Config for Steps/Machines
* Production Environment: `distributed_config_production.yaml`
* Non-Production Environment: `distributed_config_test.yaml`

***NOTE: Later we would want to get rid of hard-coded config and take DAG as an input***

# Logging
* Production Environment:
  These logs are propagated to Google Stackdriver
* Test Environment:
  These logs are propagated to Google Stackdriver
* Development Environment:
  These logs are persisted locally in the session and not propagated anywhere

# Dependencies
* Pip Packages:
  ```
   pyyaml
   ```
