#!/bin/bash

##-----------------------------------------------------------
## Vimana Processing Pipeline build script
## Date: 30/08/2017
## Authors: Madhav & Abhishek
##
## Does the following in a new packaging folder:
## 1. Checks out all code to be built and packaged.
## 2. Creates packages of all modules.
## 3. Creates uber package containing all sub-packages.
## 4. Uploads the uber package to cloud storage
## 5. Cleanup and exit
##-----------------------------------------------------------

if [ -z $1 ]; then 
    echo "Specify version number!"
    echo "Exiting..!"
    exit
fi

RELEASE_VERSION=${1}
GIT_URL_PREFIX="https://github.com/AspecScire/"
GIT_URL_SUFFIX=".git"

# Saving Git credentials for 5 minutes
# Removing this would require the user to enter username and password for every repo
git config --global credential.helper "cache --timeout=300"

## Clone a project and create a tarball for the directory
## ------------------------------------------------------
##
## Function which clones an aspecscire module in the current folder,
## removes all git related files, and then creates a tarball for the
## folder. Finally removes the folder.
function clone_and_tarball {
    PROJECT_NAME=${1}
    PROJECT_GIT_URL=${GIT_URL_PREFIX}${PROJECT_NAME}${GIT_URL_SUFFIX}
    echo "Will clone and create tarball for ${PROJECT_NAME}"
    echo "Project URL is ${PROJECT_GIT_URL}"
    git clone ${PROJECT_GIT_URL}
    cd ./${PROJECT_NAME}
    git archive -o ../${PROJECT_NAME}-v${RELEASE_VERSION}.tar.gz --prefix=${PROJECT_NAME}/ --format=tar.gz master 
    cd ../
    rm -rf ./${PROJECT_NAME}
    }

clone_and_tarball "vimana_assistant_apis"
clone_and_tarball "vimana_photoscan_automation"
clone_and_tarball "vimana-web-main"
clone_and_tarball "gcloud_functions"
clone_and_tarball "scripts"
clone_and_tarball "vimana_model_monitoring_services"
clone_and_tarball "vimana_measurement_services"
clone_and_tarball "vimana_configurations"

# TODO: Add photoscan tarball back
gsutil -m cp gs://vimana-release/photoscan-pro/photoscan-pro_1_3_4-v0.2.18.tar.gz ./
mv photoscan-pro_1_3_4-v0.2.18.tar.gz photoscan-pro-v${RELEASE_VERSION}.tar.gz

mkdir release-v${RELEASE_VERSION}
mv *${RELEASE_VERSION}.tar.gz ./release-v${RELEASE_VERSION}
# TODO: Add agents tarball
PROJECT_NAME="vimana_workbench"
git clone  ${GIT_URL_PREFIX}${PROJECT_NAME}${GIT_URL_SUFFIX}
cd ./$PROJECT_NAME
mvn clean install
cp ./dist/*.tar.gz ../release-v${RELEASE_VERSION}
cd ../
rm -rf ./$PROJECT_NAME

# TODO: Add authproxy tarball
PROJECT_NAME="authproxy"
git clone  ${GIT_URL_PREFIX}${PROJECT_NAME}${GIT_URL_SUFFIX}
cd ./$PROJECT_NAME
mvn clean install
cp ./dist/*.tar.gz ../release-v${RELEASE_VERSION}
cd ../
rm -rf ./$PROJECT_NAME

gsutil -m cp -r ./release-v${RELEASE_VERSION} gs://vimana-release/qa_releases

#clean-up 
rm -rf ./release-v${RELEASE_VERSION}

echo "Build v${RELEASE_VERSION} Complete"


