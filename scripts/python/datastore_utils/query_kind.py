from google.oauth2 import service_account
from google.cloud import datastore
import csv, os

#GCP_CRED_FILE_PATH = "/opt/gcp-config/keys/VimanaTest-38599f5ca29c.json"
#GCP_PROJECT = "vimanatest-173605"
GCP_CRED_FILE_PATH = "/opt/gcp-config/keys/prod_keyfile.json"
GCP_PROJECT = "lyrical-oath-167616"

GOOGLE_SERVICE_ACCOUNT_CREDS = service_account.Credentials.from_service_account_file(GCP_CRED_FILE_PATH)
GOOGLE_DATASTORE_CLIENT = datastore.Client(project=GCP_PROJECT,
                                           credentials=GOOGLE_SERVICE_ACCOUNT_CREDS)

KIND = "ImageMetadata"
client = GOOGLE_DATASTORE_CLIENT
o_filename = os.getcwd() + "/" + KIND + "-output.csv"


def initialize_output_file(o_filename):
    print("Output file path:", o_filename)
    try:
        os.remove(o_filename)
    except OSError:
        pass
    output_file = open(o_filename, 'w')
    output_file.close()

print("Processing...")
query = client.query(kind=KIND)
query.add_filter("user", "=", "bipin")
results = list(query.fetch())
flight_session_list = []
empty_meta_count = 0
print("Query Complete.")
if len(results) > 0:
    initialize_output_file(o_filename)
    with open(o_filename, 'w') as csvoutput:
        writer = csv.writer(csvoutput, lineterminator='\n')
        for eachResult in results:
            flight_session = eachResult.get("flight_session_guid")
            capturedAt = eachResult.get("capturedAt")
            if capturedAt is None:
                empty_meta_count += 1
                print("Empty meta! GUID: {}".format(eachResult.get("guid")))
            if flight_session is not None and flight_session not in flight_session_list:
                flight_session_list.append(flight_session)
                print("Adding flight session: {}".format(flight_session))
print("Total Entities: {}".format(len(results)))
print("Entities without meta: {}".format(empty_meta_count))
print("Flight Sessions:")
flight_session_list.sort()
print(flight_session_list)
print("Export complete")
