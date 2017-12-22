#!/bin/bash

# Check Host Machine Type Compatibility
unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    CYGWIN*)    machine=Cygwin;;
    MINGW*)     machine=MinGw;;
    *)          machine="UNKNOWN:${unameOut}"
esac

echo "Host OS Type: "${machine}

#set the fonts folder for QT (this is required for the pdf report exported at the end)
export QT_QPA_FONTDIR=/usr/share/fonts/truetype/

PATH_TO_WORKFLOW_CONTROLLER=$(dirname "$0")/vimana/photoscan_automation/photogrammetry_workflow.py

W_PHOTOSCAN="$(which photoscan)"

echo $PATH
if [[ "$W_PHOTOSCAN" =~ "photoscan" ]]; then
    echo "Found the path to PhotoScan"
else
    printf "\nPhotoscan-pro path not found in system environment variable. Please enter the directory path for photoscan.\
    \nFor Darwin, PATH is usually: /Applications/PhotoScanPro.app/Contents/MacOS/\n"
    read PPATH
    PHOTOSCAN_PATH=PATH=$PATH:$PPATH
    export $PHOTOSCAN_PATH
fi

#extract video Frames before starting automation


case "${machine}" in
    Linux*)     photoscan.sh -r -platform offscreen $PATH_TO_WORKFLOW_CONTROLLER "$@";;
    Mac*)       PhotoScanPro -r $PATH_TO_WORKFLOW_CONTROLLER "$@";;
    *)          echo "Not supported!";;
esac
