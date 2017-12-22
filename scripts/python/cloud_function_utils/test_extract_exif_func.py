import requests
import argparse
import csv
import os

GCP_FUNC_UPDATEMETADATA_URL = "https://us-central1-vimanatest-173605.cloudfunctions.net/updateMetaData"
success_count = 0
error_count = 0

def request_cloud_call(data):
    response = requests.post(GCP_FUNC_UPDATEMETADATA_URL, json=data)
    if response.status_code != 200:
        global error_count
        error_count = error_count + 1
        print("Error Encountered!")
    else:
        global success_count
        success_count = success_count + 1
    return response

def process_checksum_on_cloud(guid):
    cloud_func_req_data = {
        'file':{
            'guid': guid,
            'type': "image/jpeg",
            'user_id': "test_extract_exif_func",
        }
    }
    return request_cloud_call(cloud_func_req_data)


def initialize_output_file(o_filename):
    print("Processing...")
    print("Output file path:", o_filename)
    try:
        os.remove(o_filename)
    except OSError:
        pass
    output_file = open(o_filename, 'w')
    output_file.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file',
                        help="Path of File in csv format having guid")
    args = parser.parse_args()
    if args.file:
        o_filename = os.getcwd() + "/output.csv"
        initialize_output_file(o_filename)
        with open(args.file, "rt") as f_obj:
            with open(o_filename, 'w') as csvoutput:
                writer = csv.writer(csvoutput, lineterminator='\n')
                reader = csv.reader(f_obj)
                row_count = 0
                for row in reader:
                    row_count += 1
                    print("Processing file: ", row_count)
                    if len(row) > 0:
                        guid = row[0].strip()
                        response = process_checksum_on_cloud(guid)
                        row.append(response.status_code)
                        row.append(response.text)
                        writer.writerow(row)
                    else:
                        print("Encountered Blank entry")
                print("Total guids:", row_count)
                print("Success count:", success_count)
                print("Error count:", error_count)

    else:
        print("Input File not specified")

if __name__ == "__main__":
    main()
