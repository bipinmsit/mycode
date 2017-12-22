"""
File to test the upload API.
Mention a particular folder to this executable, that contains images to upload, and it will calculate checksum and
perform the upload of these files using the Upload APIs.
"""
import requests
import os
import csv
import sys
import pandas as pd
ACK_URL = "https://vimana.vimanalabs.com/api/v1/upload/acknowledge/"
#ACK_URL = "http://localhost:8000/api/v1/upload/acknowledge/"
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

def fix_files(input_csv=output_entity_csv):
    template = pd.read_csv(input_csv)
    data = template[["name", "guid", "entity_key"]].values
    print("Starting Processing...")
    for row in data:
        file = {
            "name": row[0],
            "guid": row[1],
            "entity_key": row[2],
        }
        fix_meta_file(file)




def fix_meta_file(file):
    print("processing file {}".format(file['name']), end='\r')
    ack_req_json = {
        "files": [
            {
                "name": file["name"],
                "guid": file["guid"],
                "entity_key": file["entity_key"]
            }
        ]
    }
    try:
        ack_resp = requests.post(ACK_URL, auth=('aspecscire', 'drone@123'), json=ack_req_json)
        ack_resp.raise_for_status()
    except:
        print("ACK request failed!")
        raise RuntimeError("Ack request failed!")
    ack_resp_json = ack_resp.json()["files"][0]
    error_dict = ack_resp_json.get("error", {})
    error_message = error_dict.get("message")
    if error_message is not None:
        handle_error_file(ack_resp_json)
    return


def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) > 1:
        input_csv_path = argv[1]
    else:
        print("Specify path to CSV with list of images to fix!")
        return 1

    initialize_output_file(o_filename)
    fix_files(input_csv_path)


    print("Upload Complete!")


if __name__ == "__main__":
    sys.exit(main())
