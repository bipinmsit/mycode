import json
import requests
import sys, os 
import hashlib
import subprocess
from pathlib import Path
import re

script_path = os.path.realpath(__file__)
python_path = os.path.dirname(os.path.dirname(os.path.dirname(script_path)))
sys.path.append(python_path)

from python.utils.common import Common

common = Common()

dir_name_list= []

def call_mapbox_upload(data: object, fullPath:str):
    try:
        mapbox_data = data
        mapbox_details = common.mapbox_api_credentials()
        mapbox_data['apiUrl'] = mapbox_details['apiUrl']
        mapbox_data['userName'] = mapbox_details['credentials']['userName']
        mapbox_data['accessToken'] = mapbox_details['credentials']['accessToken']
        json_path = fullPath + '/' + 'mapbox-metadata.json'
        filePath = fullPath + '/' + mapbox_data['fileName']
        outputMetaData = mapbox_data
        userName = outputMetaData.pop('userName')
        accessToken = outputMetaData.pop('accessToken')
        baseFileName = os.path.basename(outputMetaData['fileName'])
        fileName = os.path.splitext(baseFileName)[0]
        s = json.dumps(outputMetaData)

        # response = subprocess.call(['mapbox-upload.py', '-u', mapbox_data['userName'], mapbox_data['accessToken'], '-gm',
        #                  json.dumps(outputMetaData), '-om', json_path, filePath, outputMetaData['fileName'] ], stdout=sys.stdout, stderr=sys.stderr)
        try:
            response = subprocess.check_call(['mapbox-upload.py', '-u', userName, accessToken, '-gm',
                                              json.dumps(outputMetaData), '-om', json_path, filePath, fileName],
                                             stderr=sys.stderr, stdout=sys.stdout)
            common.logging(response)
        except Exception as ex:
            error = str(ex)
            common.logging(error)


    except Exception as ex:
        error = str(ex)
        common.logging(error)




def md5Checksum(filePath):
    with open(filePath, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()

def publishFiles(inputData: object, dir_path: str, api_url):
    try:
        for _file in inputData['files']:
            full_path = ''

            if _file["name"].lower() in "photoscan.zip":
                full_path = os.path.join(dir_path, inputData['filePath'], _file["name"])
                ps_folder_name = re.sub('\.zip$', '', _file["name"])
                print(ps_folder_name)
                source_dir = os.path.join(dir_path, inputData['filePath'], ps_folder_name)
                print(source_dir)
                common.make_zipfile(full_path, source_dir)
                print('zip file is created successfully')
            else:
                full_path = os.path.join(dir_path, inputData['filePath'], _file["directory"], _file["name"])




            print(full_path)
            if os.path.isfile(full_path):
                print(full_path)
                data = {}
                data['fileName'] = _file["name"]
                data['ancestor'] = inputData["ancestor"]
                data['fileCheckSum'] = md5Checksum(full_path)

                if "output" in full_path.lower():
                    cwd = os.path.join(dir_path, inputData['filePath'], _file["directory"])
                    if data['fileName'].lower().endswith('-dem.tif'):
                        data['type'] = 'dem'
                        data['fileType'] = 'image/tiff'
                    elif data['fileName'].lower().endswith('-mosaic.tif'):
                        data['type'] = 'mosaic'
                        data['fileType'] = 'image/tiff'
                        print('This %s ortho mosaic is going to upload mapbox' % (data['fileName']))
                        # call_mapbox_upload(data, cwd)
                    elif data['fileName'].lower().endswith('-colorshaded.tif'):
                        data['type'] = 'tileset'
                        data['fileType'] = 'image/tiff'
                        print('This %s colorshaed dem is going to upload mapbox' % (data['fileName']))
                        call_mapbox_upload(data, cwd)
                        print('The process is going on')
                        return True

                    elif data['fileName'].lower().endswith('-dtm.tif'):
                        data['type'] = 'dtm'
                        data['fileType'] = 'image/tiff'
                elif "execution reports" in full_path.lower():
                    if data['fileName'].lower().endswith('-execrep.*'):
                        data['type'] = 'execrep'
                        data['fileType'] = 'image/pdf'
                    elif data['fileName'].lower().endswith('-execrep.xls'):
                        data['type'] = 'psrep'
                        data['fileType'] = 'application/vnd.ms-excel'
                elif "photoscan reports" in full_path.lower():
                    if data['fileName'].lower().endswith('-psrep.pdf'):
                        data['type'] = 'psrep'
                        data['fileType'] = 'application/pdf'
                    elif data['fileName'].lower().endswith('-psrep.xls'):
                        data['type'] = 'psrep'
                        data['fileType'] = 'application/vnd.ms-excel'
                    elif data['fileName'].lower().endswith('-psrep.txt'):
                        data['type'] = 'psrep'
                        data['fileType'] = 'text/plain'
                if data['fileName'].lower() in "photoscan.zip":
                    data['type'] = 'photoscan'
                    data['fileType'] = 'application/zip'

                print(json.dumps(json.dumps(data)))
                query = '''
                {
                    sas(name: ''' + json.dumps(json.dumps(data)) + '''){
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
                response = requests.get(api_url + query)
                content = response.json()
                print(content)
                if content["data"]["sas"]["status"] == True:
                    headers = {'content-type': 'application/octet-stream'}
                    # files = {'file': open(full_path, 'rb')}
                    print('file uploading started')
                    try:
                        with open(full_path, 'rb') as local_file:
                            common.logging('File uploading started %s this file.' % (data['fileName']))
                            upload_api_url = content["data"]["sas"]["fileUrl"]
                            upload_response = requests.put(upload_api_url, data= local_file, headers= headers)
                            common.logging('File uploading completed %s this file.' % (data['fileName']))
                            print('file uploading completed')
                            print(upload_response)

                        # common.logging('File uploading started %s this file.' % (data['fileName']))
                        # r = requests.put(content["data"]["sas"]["fileUrl"], files=files, headers=headers)
                        # common.logging('File uploading completed %s this file.' % (data['fileName']))
                        # print('file uploading completed')
                        # print(r)
                    except Exception as ex:
                        print('file uploading error')
                        common.logging('Error occured while uploading %s this file. ' %(data['fileName']))
                        error = str(ex)
                        common.logging(error)


                elif content["data"]["sas"]["status"] == False:
                    print("This %s file alrdeay uploaded" % (data['fileName']))

        return True

    except Exception as ex:
        error = str(ex)
        common.logging(error)
        return  False


def dir_to_list(dirname:str, path=os.path.pathsep):
    data = []
    print(dirname, path)
    # print(os.getcwd())
    for name in os.listdir(dirname):
        dct = {}
        dct['name'] = name

        full_path = os.path.join(dirname, name)
        if os.path.isfile(full_path):
            dct['fileCheckSum'] = md5Checksum(full_path)
            dct['type'] = 'file'

        elif os.path.isdir(full_path):
            dct['type'] = 'directory'

            if dct['name'] == "Photoscan":
                dct['name'] = dct['name'] + '.zip'
                dct['type'] = 'file'
                dct['fileCheckSum'] = None
                # ps_files = {
                #     'name': dct['name'] + '.zip',
                #     'fileCheckSum': '',
                #     'type': 'file'
                # }
                # dct['children'] = [ps_files]

            else:
                dct['children'] = dir_to_list(full_path, path=path + name + os.path.pathsep)

        # Photoscan folder already added as zip file so if Photoscan.zip file is exists we are not using that file
        if(name != "Photoscan.zip"):
            data.append(dct)


    return data


def help():
    print("Usage:- copy_script.py <options>\n"\
          "     <options> can include ->\n"\
          "     -h,--help                                   -> print this help message\n"\
		  "     -md,--metadata <metadata>                   -> Metadata for copy the files\n"          
		  "     However, access-token and username should correspond. " )

def main(argv=None):
    argv = sys.argv
    options = argv[1:]
    metadata = None

    if (argv.count('-h') > 0) or (argv.count('--help')) > 0:
        help()
        return -1

    # For '-md,--metadata'
    if options.count('-md') > 0 :
        md_idx = options.index('-md')
        if len(options[md_idx:]) < 2:
            print('Error. Specify Metadata \nCheck help with "-h"', file=sys.stdout)
            print('Error. Metadata is not specified. ', file=sys.stderr)
            sys.exit(1)
        else:
            metadata = options[md_idx + 1]
    elif options.count('--metadata') > 0 :
        md_idx = options.index('--metadata')
        if len(options[md_idx:]) < 2:
            print('Error. Specify Metadata \nCheck help with "-h"', file=sys.stdout)
            print('Error. Metadata is not specified. ', file=sys.stderr)
            sys.exit(1)
        else:
            metadata = options[md_idx + 1]


    if metadata is None:
        print('ERROR 1. No MetaData is obtained.', file=sys.stdout)
        print('ERROR 1. No MetaData is obtained.', file=sys.stderr)
    else:
        data = eval(metadata)
        print(data)
        if isinstance(data, dict):
            api_url = data['api_url']
            file_url = data['file_url']
            parents = data['ancestor']
            root_dir = common.project_path()
            # print('file_url', file_url)
            # dir_files = json.dumps(dir_to_list(root_dir + file_url))
            dir_files = dir_to_list(root_dir + file_url)
            files = []
            print( dir_files)

            print( isinstance(dir_files, list) )

            for _dir in dir_files :
                print(_dir)
                if _dir['name'] == 'Output':
                    for _file in _dir['children']:
                        _file['directory'] = _dir['name']
                        files.append(_file)
                elif _dir['name'] == 'Photoscan.zip':
                    files.append(_dir)
                elif _dir['name'] == 'Project Reports':
                    for psrep in _dir['children']:
                        if psrep['name'] == 'Execution Reports':
                            for _file in psrep['children']:
                                _file['directory'] = _dir['name'] + '/' + psrep['name']
                                files.append(_file)
                        elif psrep['name'] == 'Photoscan Reports':
                            for _file in psrep['children']:
                                _file['directory'] = _dir['name'] + '/' + psrep['name']
                                files.append(_file)


            inputData = {
                'ancestor': ['Site', int(parents['Site']), 'Stage', int(parents['Stage'])],
                'session': int(parents['Session']),
                'files': files,
                'filePath': file_url
            }

            print('inputData', inputData)

            query = '''
                {
                  publish(data: ''' + json.dumps(json.dumps(inputData)) + ''') 
                }
                '''
            print(api_url)
            print(query)

            response = common.makeapi_call(query, api_url)
            print('publish response', response)

            publish_input_data = json.loads(response['data']['publish'])
            publishFiles(publish_input_data, root_dir, api_url)
            sys.exit(0)

#start process
if __name__ == '__main__':
    main()
