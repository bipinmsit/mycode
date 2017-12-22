"""
File to test the upload API.
Mention a particular folder to this executable, that contains images to upload, and it will calculate checksum and
perform the upload of these files using the Upload APIs.
"""
import requests
import os
import csv
import sys
import glob
import hashlib
import pandas as pd
CREATE_URL = "https://vimana.vimanalabs.com/api/v1/upload/create/"
#CREATE_URL = "http://localhost:8000/api/v1/upload/create/"
INPUT_IMAGE_FOLDER = sys.argv[1]
o_filename = os.getcwd() + "/upload_test_output.csv"
output_entity_csv = os.getcwd() + "/list_entity_ack.csv"

def initialize_output_file(out_filename, columns=["file_name", "file_checksum", "file_guid", "error"]):
    print("Output file path:", out_filename)
    try:
        os.remove(out_filename)
    except OSError:
        pass

    with open(out_filename, 'w') as output_file:
        writer = csv.writer(output_file, lineterminator='\n')
        writer.writerow(columns)
    return


def handle_error_file(u_file):
    name = u_file.get("name")
    checksum = u_file.get("checksum")
    guid = u_file.get("guid")
    error_dict = u_file.get("error", {})
    error_code = error_dict.get("code", "")
    error_message = error_dict.get("message", "")
    error = "code:{0} message:{1}".format(error_code, error_message)
    row_to_write = [name, checksum, guid, error]
    write_row_in_csv(row_to_write)


def write_row_in_csv(row):
    with open(o_filename, 'a') as csvoutput:
        writer = csv.writer(csvoutput, lineterminator='\n')
        writer.writerow(row)


def process_file_list(file_list):
    """
    Function to process a list of files to be uploaded.
    Args:
        file_list: List of files to be processed

    Returns:
    """
    upload_req_json = {
        "checksum_algo": "md5",
        "files": [],
    }
    print("Starting process!")
    for file in file_list:
        file_dict = create_upload_req(file)
        upload_req_json['files'].append(file_dict)


    try:
        upload_resp = requests.post(url=CREATE_URL, json=upload_req_json, auth=('aspecscire', 'drone@123'))
        upload_resp.raise_for_status()
        upload_resp_json = upload_resp.json()
    except Exception as excpt:
        print("Request to CREATE URL failed!")
        raise RuntimeError(excpt)

    files_to_upload = upload_resp_json.get("files")
    if files_to_upload is None:
        raise RuntimeError("Files list empty in response from upload create req!")

    columns = ["name", "guid", "entity_key"]
    data_list = []
    for file in files_to_upload:
        print(file['name'], end="\r")
        if file['error'].get("code") == "E_UPLOAD_CREATE_FILE_EXISTS":
            data_list.append([file['name'], file['guid'], file['entity_key']])

    dataframe = pd.DataFrame(data_list, columns=columns)
    dataframe.to_csv(output_entity_csv)
    print("Write to CSV complete!")




def get_file_checksum(u_file):
    """
    Function to get the md5 checksum of a file.
    Args:
        u_file:

    Returns:

    """
    print(u_file)
    with open(u_file, 'rb') as file_to_read:
        data = file_to_read.read()
        file_md5_checksum = hashlib.md5(data).hexdigest()

    return file_md5_checksum


def create_upload_req(u_file):
    """
    Function to process a single file.
    Args:
        u_file:

    Returns:

    """
    file_name = os.path.basename(u_file)
    file_checksum = get_file_checksum(u_file)
    file_dict = {
        "name": file_name,
        "checksum": file_checksum,
    }
    return file_dict


def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) > 1:
        input_image_folder = argv[1]
    else:
        print("Specify folder where input images are present!")
        return 1

    file_list = glob.glob(os.path.join(input_image_folder, "*.JPG"))
    file_list.sort()
    print("No. of files to be processed are: {}".format(len(file_list)))
    initialize_output_file(o_filename)
    process_file_list(file_list)


    print("Upload Complete!")


if __name__ == "__main__":
    sys.exit(main())
