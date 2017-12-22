from google.oauth2 import service_account
from google.cloud import datastore

GCP_CRED_FILE_PATH = "/opt/gcp-config/keys/VimanaTest-38599f5ca29c.json"
GCP_PROJECT = "vimanatest-173605"

GOOGLE_SERVICE_ACCOUNT_CREDS = service_account.Credentials.from_service_account_file(GCP_CRED_FILE_PATH)
GOOGLE_DATASTORE_CLIENT = datastore.Client(project=GCP_PROJECT,
                                           credentials=GOOGLE_SERVICE_ACCOUNT_CREDS)

#KIND = "UploadedRawData"
KIND = "ImageMetadata"
#KIND = "ProcessingSession"
#KIND = "Workflow"
#KIND = "FlightSession"

client = GOOGLE_DATASTORE_CLIENT

query = client.query(kind=KIND)
query.keys_only()

results = list(query.fetch())
print("Query Complete. Beginning delete....")
while len(results) > 0:
    batch = client.batch()
    batch.begin() 
    for i in range(100):
        print('.', end='')
        if len(results) == 0:
            break
        batch.delete(results.pop().key)
    print('|')
    batch.commit()
#print("Batching done! Send Delete request!")
print("Delete complete")
query = client.query(kind=KIND)
query.keys_only()
results = list(query.fetch())
if len(results) > 0:
    import pdb;pdb.set_trace()

    
