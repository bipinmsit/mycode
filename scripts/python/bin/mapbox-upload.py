#!/usr/bin/env python

import sys
import boto3
import requests
import json
import time
import csv
def upload_tileset(tileset_loc,tileset_name,username='madhavm',
 				   access_token='sk.eyJ1IjoibWFkaGF2bSIsImEiOiJjajNi' + \
     			   'ZnZnbW4wMDVpMndvNzNqNGJtNTRlIn0.nksdjKYVYr7U4F-nmVt7_w'):
	"""
	Function to upload a tileset to Mapbox.
	Once a tileset is uplaoded to Mapbox, it is referenced through way of its
	MapID or name. This must be saved in another location, or variable, as this is 
	required to pull up Metdata of the correspoding tileset.

	Function will return MapID, as string.
	"""				
	upload_req_url = 'https://api.mapbox.com/uploads/v1/' + username + '/credentials?access_token=' + access_token
	s3_upload_resp = None
	for i in range(10):
		try:
			s3_upload_req = requests.post(upload_req_url)
			s3_upload_req.raise_for_status()
			print(s3_upload_req)
			s3_upload_resp = s3_upload_req.json()
			break
		except requests.exceptions.HTTPError as err:
			print(err,file=sys.stderr)
			continue
		except requests.exceptions.Timeout as err:
			# Maybe set up for a retry, or continue in a retry loop
			print('Timeout Error', file=sys.stderr)
		except requests.exceptions.TooManyRedirects as err:
			# Tell the user their URL was bad and try a different one
			print(err, file=sys.stderr)
			print("Upload Request URL used is bad.\nURL=" + upload_req_url,file=sys.stderr)
		except requests.exceptions.RequestException as e:
			# catastrophic error. bail.
			print(e)
			print('Catastrophic Error. Exiting..',file=sys.stderr)
			sys.exit(1)
		
	if s3_upload_resp is None:
		print('Error. Check input details, and try again.',file=sys.stdout)
		print('Error. Could not get response from MapBox Server'\
				' with curent credentials and data.',file=sys.stderr)
		sys.exit(1)

	s3_client = boto3.client('s3',aws_access_key_id = s3_upload_resp['accessKeyId'],
	    						  aws_secret_access_key = s3_upload_resp['secretAccessKey'],
	    						  aws_session_token = s3_upload_resp['sessionToken'],
	)
	print('S3-URL=' + s3_upload_resp['url'])
	print('Starting S3 Upload...')
	#Filename must also be changed as necessary
	try:
		with open(tileset_loc, 'rb') as data:
			s3_client.upload_fileobj(data, s3_upload_resp['bucket'], s3_upload_resp['key'])
	except FileNotFoundError as err:
		print('File not found in mentioned directory',file=sys.stdout)
		print('File not found in mentioned directory',file=sys.stderr)
		print(err,file=sys.stderr)
		sys.exit(1)
	except Exception as err:
			print(err,file=sys.stderr)
			sys.exit(1)


	tileset_name_str = username + '.' + tileset_name
	
	payload = {
		'tileset': tileset_name_str, #Must be changed dynamically, so that tileset data is not replaced. 
		'url': s3_upload_resp['url'],
		'name': tileset_name #Must be changed dynamically as well, or can be left blank. 
	}

	print('Staging Upload to S3 Complete...\nCreating Upload to MapBox..')
	try:
		mb_upload_req_url = 'https://api.mapbox.com/uploads/v1/' + username + '?access_token=' + access_token
		mapbox_upload_req = requests.post(mb_upload_req_url,json=payload)
		mapbox_upload_req.raise_for_status()
		mapbox_upload_resp = mapbox_upload_req.json()
		print("upload ID=" + mapbox_upload_resp['id'])
	except Exception as err:
		print(err,file=sys.stderr)
		sys.exit(1)

	if(mapbox_upload_resp['error']!=None):
		#Log error somewhere and exit from function
		err = mapbox_upload_resp['error']
		print('MapBox upload error occurred.\n' + err, file=sys.stderr)
		sys.exit(1)
		
	else:
		#Waiting for mapbox upload to complete and see if any errors are thrown. 
		mb_upload_stat_url = 'https://api.mapbox.com/uploads/v1/' + username + '/' + mapbox_upload_resp['id'] + '?access_token=' + access_token
		upload_finished = False
		while not upload_finished:
			time.sleep(5)	
			mapbox_upload_stat = requests.get(mb_upload_stat_url)
			mapbox_upload_stat_resp = mapbox_upload_stat.json()
			#Progress variable in response does not work as intended, hence removed
			#print('Progress=' + str(float(mapbox_upload_stat_resp['progress'])*100))
			print(".",end="\n")
			if mapbox_upload_stat_resp['error'] != None:
				err = mapbox_upload_stat_resp['error']
				print('\nError encountered.\n'+err,file=sys.stderr)
				sys.exit(1)
			if mapbox_upload_stat_resp['complete'] == True:
				upload_finished = True
				print('Upload to MapBox complete...')			
				break

def upload_google_meta(gMetaJSON,mapboxMetaJSON):
	#Write code to upload mapboxMetaJSOn to Google Datastore, with all necesary field
	gJSON = json.loads(gMetaJSON)
	gJSON['metaData'] = mapboxMetaJSON
	api_url = gJSON.pop("apiUrl")

	query = '''
            {
                sas(name: '''+ json.dumps(json.dumps(gJSON)) + '''){
                  name
                  type
                  createdAt
                  modifiedAt
                  fileUrl
                  fileType
                  status
                }
            }        
            '''
	response = requests.get(api_url+'?query='+ query)
	content = response.json()
	pass	





def get_tileset_meta(tileset_name,outputFile=None,username='madhavm', access_token='sk.eyJ1IjoibWFkaGF2bSIsImEiOiJjajNiZnZnbW4wMDVpMndvNzNqNGJtNTRlIn0.nksdjKYVYr7U4F-nmVt7_w' ):
	tileset_name_str = username + '.' + tileset_name
	mb_meta_req_url = 'https://api.mapbox.com/v4/' + tileset_name_str + '.json?access_token=' + access_token
	mapbox_meta_resp = None
	for i in range(10):
		try:
			mapbox_meta_req = requests.get(mb_meta_req_url)
			mapbox_meta_req.raise_for_status()
			mapbox_meta_resp = mapbox_meta_req.json()
			print(mapbox_meta_req)
			break
		except requests.exceptions.HTTPError as err:
			print(err,file=sys.stderr)
			continue
		except requests.exceptions.Timeout as err:
			# Maybe set up for a retry, or continue in a retry loop
			print('Timeout Error', file=sys.stderr)
		except requests.exceptions.TooManyRedirects as err:
			# Tell the user their URL was bad and try a different one
			print(err, file=sys.stderr)
			print("Request URL used is bad.\nURL=" + upload_req_url,file=sys.stderr)
		except requests.exceptions.RequestException as err:
			# catastrophic error. bail.
			print(err)
			print('Catastrophic Error. Exiting..',file=sys.stderr)
			sys.exit(1)
	if mapbox_meta_resp is None:
		print('Error. Check input details, and try again.',file=sys.stdout)
		print('Error. Could not get response from MapBox Server'\
			  ' with curent credentials and data.',file=sys.stderr)
		sys.exit(1)
	#Writing Metadata to output File
	#Note that writing to JSON dumps the entire mapbox meta response
	outputCSV = None
	outputJSON = None
	if outputFile is None:
		print('Warning. Specify a output file to write Metadata',file=sys.stdout)
		print("Warning. No meta file specified. ",file=sys.stderr)
	elif outputFile.find('.csv') >= 0:
		outputCSV = outputFile
		#Writing to CSV
		with open(outputCSV,mode='w') as f:
			w = csv.writer(f)
			w.writerow(['','Longitude/Zoom Level','Latitude','Native Zoom'])
			w.writerow(['center',str(mapbox_meta_resp['center'][0]),str(mapbox_meta_resp['center'][1]),
						str(mapbox_meta_resp['center'][2])])
			w.writerow(['MinZoom',mapbox_meta_resp['minzoom']])
			w.writerow(['MaxZoom',mapbox_meta_resp['maxzoom']])
			w.writerow(['userName',username])
			w.writerow(['Tileset Name',tileset_name])
			f.close()
		print('Done.\nOutput Meta stored in CSV file at ' + outputCSV,file=sys.stdout)
	
	elif outputFile.find('.json') >= 0:
		outputJSON = outputFile
		with open(outputJSON,mode='w') as json_f:
			json.dump(mapbox_meta_resp,json_f)
			json_f.close()
	



	meta = [tileset_name, mapbox_meta_resp['center'], mapbox_meta_resp['minzoom'],mapbox_meta_resp['maxzoom'] ]
	return mapbox_meta_resp, meta

def help():
    print("Usage:- mapbox-upload.py <options> <Tileset-Location> <Tileset-Name>\n"\
          "     <options> can include ->\n"\
          "     -h,--help                                   -> print this help message\n"\
		  "     -u,--username <UserName> <access-token>     -> Custom Username and Access token\n"\
          "     -a,--access_token <access-token>            -> Use custom Access Token\n" \
		  "     -om,--output_meta <Meta File>               -> CSV/JSON file to store output meta data\n"\
		  "     -gm,--gds_meta <JSON string>                -> JSON string containing Metadata for GDS Meta upload"
		  "Note:Default UserName and Access token can be edited in Python Script	\n"\
		  "     However, access-token and username should correspond. " )
def main(argv=None):
	argv=sys.argv
    #Add functionality to sanity check commands passed through this
	options = argv[1:-2]
	data = argv[-2:]
	username = None
	access_token = None
	if (argv.count('-h') > 0) or (argv.count('--help')) > 0:
		help()
		return -1

	if len(argv) < 3:
        #When there are not enough arguments to use the command
		print("Use '-h' to view help",file=sys.stdout)
		print("ERROR 1. Not enough arguments",file=sys.stderr)
		return 1

	tile_loc = data[0]
	tile_name = data[1]	
	#For '-u,--username'
	if options.count('-u') > 0:  
		u_idx = options.index('-u')
		if len(options[u_idx:]) < 3:
			print('Error. Specify Username and corresponding access token\nCheck help with "-h"',file=sys.stdout)
			print('Error. Username and corresponding access token not specified. ',file=sys.stderr)
			sys.exit(1)
		else:
			username = options[u_idx + 1]
			access_token = options[u_idx + 2] 

	elif options.count('--username') > 0:
		u_idx = options.index('--username')
		if len(options[u_idx:]) < 3:
			print('Error. Specify Username and corresponding access token\nCheck help with "-h"',file=sys.stdout)
			print('Error. Username and corresponding access token not specified.',file=sys.stderr)
			sys.exit(1)
		else:
			username = options[u_idx + 1]
			access_token = options[u_idx + 2] 
	#For '-a,--access-token'
	if options.count('-a') > 0:  
		a_idx = options.index('-a')
		if len(options[a_idx:]) < 2:
			print('Error. Specify Access token\nCheck help with "-h"',file=sys.stdout)
			print('Error. Access token not specified. ',file=sys.stderr)
			sys.exit(1)
		else:
			access_token = options[a_idx + 1] 

	elif options.count('--access_token') > 0:
		a_idx = options.index('--access_token')
		if len(options[u_idx:]) < 3:
			print('Error. Specify access token\nCheck help with "-h"',file=sys.stdout)
			print('Error. Access token not specified.',file=sys.stderr)
			sys.exit(1)
		else:
			access_token = options[a_idx + 1]
	
	#For output metadata as csv file
	meta_file = None
	if options.count('-om') > 0:
		m_idx = options.index('-om')
		if len(options[m_idx:]) < 2:
			print('Error. Specify CSV file to store output meta data.\n Check help with "-h"',file=sys.stdout)
			print('Error. Output CSV file for meta data not specified.',file=sys.stderr)
			sys.exit(1)
		else:
			meta_file = options[m_idx + 1]
		
	elif options.count('--output_meta') > 0: 
		m_idx = options.index('--output_meta')
		if len(options[m_idx:]) < 2:
			print('Error. Specify CSV file to store output meta data.\n Check help with "-h"',file=sys.stdout)
			print('Error. Output CSV file for meta data not specified.',file=sys.stderr)
			sys.exit(1)
		else:
			meta_file = options[m_idx + 1]

	#For Uploading Metadata to Google Cloud Storage		
	google_upload_meta = None
	if options.count('-gm') > 0:
		g_idx = options.index('-gm')
		if len(options[g_idx:]) < 2:
			print('Error. Specify JSON string for Google DataStore Meta Upload.\n Check help with "-h"',file=sys.stdout)
			print('Error. JSON string for Google DataStore Meta upload not specified.',file=sys.stderr)
			sys.exit(1)
		else:
			google_upload_meta = options[g_idx + 1]
		
	elif options.count('--gds_meta') > 0: 
		g_idx = options.index('--gds_meta')
		if len(options[g_idx:]) < 2:
			print('Error. Specify JSON string for Google DataStore Meta Upload.\n Check help with "-h"',file=sys.stdout)
			print('Error. JSON string for Google DataStore Meta upload not specified.',file=sys.stderr)
			sys.exit(1)
		else:
			google_upload_meta = options[g_idx + 1]
		
	

	if access_token is None:
		upload_tileset(tile_loc,tile_name)
		meta_json, meta_list = get_tileset_meta(tile_name,meta_file)
	elif username is None:
		upload_tileset(tile_loc,tile_name,access_token=access_token)
		meta_json, meta_list = get_tileset_meta(tile_name,meta_file,access_token=access_token)
	else:
		upload_tileset(tile_loc,tile_name,username,access_token)
		meta_json, meta_list = get_tileset_meta(tile_name,meta_file,username=username,access_token=access_token)
	
	if meta_json is None:
		print('ERROR 1. No MetaData obtained. Check data input and mapbox upload status.',file=sys.stdout)
		print('ERROR 1. No MetaData obtained. Check data input and mapbox upload status.',file=sys.stderr)
	else:
		try:
			upload_google_meta(gMetaJSON=google_upload_meta,mapboxMetaJSON=meta_json)
		except Exception as err:
			print('The following error occurred while uploading metadata to Google Datastore - ')
			print(err)
			sys.exit(1)
	print('\nMeta data upload complete..\nDone.')

if __name__ == "__main__":
	sys.exit(main())