# Vimana Photoscan Automation

This is the repository to handle photoscan workflow automation. 

## Running Instructions

To run photoscan 
1. Set up the directory with the following format:
```
-- Project_folder
    --Images
        -- <Contains all images>
    --Input
        -- markers-to-import.csv
    --workflow-config.json 
```

2. Run the automation script:
```
$ cd <path/to/Project_folder>
$ <path/to/this/repo>/run_photoscan_automation.sh workflow_config <development/test/production> &

```
