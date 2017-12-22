#! /usr/bin/env python3

import subprocess
import json
import os.path
import time
import argparse
import sys


def get_gsutil_installed_path():
    try:
        gsutil_installation_path = subprocess.check_output(['which', 'gsutil'])
        print("gsutil utility found!")
        return gsutil_installation_path.decode("utf-8").strip()
    except Exception as e:
        print("gsutil utility not found, Exiting!")
        raise Exception("GSUtil Utility Not Found!" + str(e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Arguments for Restoring GS Project on a local System")
    parser.add_argument("-p", "--gs_project_name", help="Google Storage Project Name", required=True)
    parser.add_argument("-b", "--project_bucket", help="GCloud Projects Bucket Path", default="vimana-project-files")
    parser.add_argument("-path", "--local_path", help="Local Path of Project(Without ending /)", required=True)
    args = vars(parser.parse_args())

    PROJECT_NAME = args["gs_project_name"]
    PROJECT_FILES_BUCKET = args["project_bucket"]
    LOCAL_PATH = args["local_path"]
    GCLOUD_PREFIX = 'gs://'
    WORKFLOW_FILE_NAME = 'workflow-files.json'
    FILES_PATHS = 'files-paths.txt'

    start = time.time()
    try:
        gsutil_path = get_gsutil_installed_path()
        print(LOCAL_PATH)
        subprocess.Popen(['ls',LOCAL_PATH]).wait()
        copy_status = subprocess.Popen(
            [gsutil_path, '-q', '-m', 'cp', '-r', 'gs://{}/{}/*'.format(PROJECT_FILES_BUCKET, PROJECT_NAME), LOCAL_PATH]).wait()
        image_dir_status = subprocess.Popen(
            [gsutil_path, 'stat', 'gs://{}/{}/Images/'.format(PROJECT_FILES_BUCKET, PROJECT_NAME)]).wait()
        print(image_dir_status)

        # Images/ dir is not present
        if image_dir_status != 0:
            IMAGES_PATH = os.path.join(LOCAL_PATH, 'Images')
            if not os.path.exists(IMAGES_PATH):
                os.makedirs(IMAGES_PATH)
                print("Local Image dir created at: " + IMAGES_PATH)
            print("Image dir restored from cloud at: " + IMAGES_PATH)

            # Initial Number of Files in IMAGES_PATH
            initial_image_count = len(
                [name for name in os.listdir(IMAGES_PATH) if os.path.isfile(os.path.join(IMAGES_PATH, name))])
            json_data = open(os.path.join(LOCAL_PATH, WORKFLOW_FILE_NAME)).read()
            data = json.loads(json_data)
            print("Loaded files json")

            # if images folder not present
            with open(os.path.join(LOCAL_PATH, FILES_PATHS), 'w') as f:

                for eachData in data:
                    # Write to the file
                    f.write(os.path.join(GCLOUD_PREFIX, eachData['bucketName'], eachData['blobId']))
                    f.write('\n')

                # Close the connection to the file
                f.close()
            print("Created Local File Path file")
            cat_output = subprocess.Popen(['cat', os.path.join(LOCAL_PATH, FILES_PATHS)], stdout=subprocess.PIPE)
            download_files_output = subprocess.Popen([gsutil_path, '-q', '-m', 'cp', '-I', IMAGES_PATH],
                                                     stdin=cat_output.stdout, stdout=subprocess.PIPE)
            cat_output.stdout.close()
            output = download_files_output.communicate()[0]
            cat_output.wait()

            print("Downloaded files using file path content")

            # Rename Files
            for eachData in data:
                # Create needed targetPath as required in Workflow-Config to Store Files
                if not os.path.exists(os.path.join(LOCAL_PATH, eachData['targetPath'])):
                    os.makedirs(os.path.join(LOCAL_PATH, eachData['targetPath']))
                os.rename(
                    os.path.join(LOCAL_PATH, 'Images', eachData['blobId'].split('/')[-1]),
                    os.path.join(LOCAL_PATH, eachData['targetPath'], eachData['fileName'])
                )
            print("Renamed files")

            # Final Number of Files in IMAGES_PATH
            final_image_count = len(
                [name for name in os.listdir(IMAGES_PATH) if os.path.isfile(os.path.join(IMAGES_PATH, name))])

            print("Elapsed Time: %s" % (time.time() - start))
            # Sanity Check for All files downloaded provided in WORKFLOW_FILE
            if abs(final_image_count-initial_image_count) != len(data):
                raise Exception("Unequal Image Count! Cloud:"
                                + initial_image_count + " Restore:"
                                + final_image_count + " workflow-files:" + len(data))

            # delete temp files-paths container file
            os.remove(os.path.join(LOCAL_PATH, FILES_PATHS))
            sys.exit(0)

    except Exception as e:
        print("Failed Restoring Project!, Error: {}".format(str(e)))
        print(sys.exc_info()[0])
        sys.exit(1)
