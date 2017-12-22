import boto3
import requests
s3_upload_req = requests.post('https://api.mapbox.com/uploads/v1/madhavm/credentials?access_token=sk.eyJ1IjoibWFkaGF2bSIsImEiOiJjajNiZnZnbW4wMDVpMndvNzNqNGJtNTRlIn0.nksdjKYVYr7U4F-nmVt7_w')
print(s3_upload_req)
s3_upload_resp = s3_upload_req.json()

s3_client = boto3.client('s3',
	aws_access_key_id = s3_upload_resp['accessKeyId'],
    aws_secret_access_key = s3_upload_resp['secretAccessKey'],
    aws_session_token = s3_upload_resp['sessionToken'],
)

#Filename must also be changed as necessary
with open('./60mts/CS_test.tiff', 'rb') as data:
	s3_client.upload_fileobj(data, s3_upload_resp['bucket'], s3_upload_resp['key'])

payload = {
  'tileset': 'madhavm.test2', #Must be changed dynamically, so that tileset data is not replaced. 
  'url': s3_upload_resp['url'],
  'name': 'test2' #Must be changed dynamically as well, or can be left blank. 
}

p = requests.post('https://api.mapbox.com/uploads/v1/madhavm?access_token=sk.eyJ1IjoibWFkaGF2bSIsImEiOiJjajNiZnZnbW4wMDVpMndvNzNqNGJtNTRlIn0.nksdjKYVYr7U4F-nmVt7_w',json=payload)
p_data = p.json()



requests.get('https://api.mapbox.com/v4/madhavm.test.json?access_token=sk.eyJ1IjoibWFkaGF2bSIsImEiOiJjajNiZnZnbW4wMDVpMndvNzNqNGJtNTRlIn0.nksdjKYVYr7U4F-nmVt7_w')