import os
import sys
import json
import copy
import hashlib
import requests
import subprocess
import getpass

script_path = os.path.realpath(__file__)
python_path = os.path.dirname(os.path.dirname(os.path.dirname(script_path)))
sys.path.append(python_path)

from python.utils.common import Common
from python.utils.utils_graphql import GraphQlObject as gql
from python.utils.db_log import *

common = Common()
folder = json.load(open(os.path.dirname(script_path) + '/config/folder-structure.json'))
folder_structure = folder['common']

def copy_files(parents, api_url, vm_details, vm_windows = False):
    siteId = str(parents['Site'])
    stageId = str(parents['Stage'])
    sessionId = str(parents['Session'])

    session_aoi_query = gql.session_aoi_query(parents)
    response = common.makeapi_call(session_aoi_query, api_url)

    client = copy.deepcopy(folder_structure)
    site_data = response['data']['site']
    stage_data = site_data['stage']
    stage = copy.deepcopy(folder_structure)
    stage['name'] = stage_data['name']
    session_files_data =None
    aoi_files_data = None
    session_data = stage_data['session']
    session_artifacts = session_data['artifacts']
    session = copy.deepcopy(folder_structure)
    session['name'] = session_data['name']
    aois_data = stage_data['aois']
    session_id = int(sessionId)
    aoi_list = copy.deepcopy(aois_data)
    aoi_response = find_aoi(session_id, aoi_list)
    aoi_artifcats = []

    if aoi_response['status'] == True:
        aoi_id = aoi_response['aoi_id']
        aoi_artifcats = aoi_response['aoi_artifacts']

    if len(session_artifacts) >0:
        session_files_response = session_list_artifacts(session_artifacts)
        session_files_data = session_files_response['children']
        aois_files_response = aoi_list_artifacts(aoi_artifcats)
        aoi_files_data = aois_files_response['children']
        session['file'] = aois_files_response['photoscan_files'] + session_files_response['session_files']
        session['children'] = session_files_data + aoi_files_data

    # append session list to stage children
    stage['children'].append(session)
    site = folder_structure
    site['name'] = site_data['name']
    # append stage to site children
    site['children'].append(stage)
    client['name'] = site_data['clientName']
    # append site to client children
    client['children'].append(site)

    site_name = site['name']
    stage_name = stage['name']
    grouping = session['name']

    if vm_windows == "False":
        # Updating status on database for copying files
        process_name = 'CopyingFiles'
        update_process_status(process_name, site_name, stage_name, grouping)
        update_process_log(process_name, vm_details['vm_name'], vm_details)

    dir_path = None
    if vm_windows == "True":
        dir_path = common.project_path_windows()
    else:
        dir_path = common.project_path()

    createDirBasedJson(client, dir_path, api_url)
    print('vm_windows',vm_windows)

    if vm_windows == "True":
        print('This is windows vm so files copied successfully.')
        return True

    try:
        common.logging(getpass.getuser())

        # Updating status on database for starting photoscan
        process_name = 'StartingPhotoScan'
        update_process_status(process_name, site_name, stage_name, grouping)
        update_process_log(process_name, vm_details['vm_name'], vm_details)

        session_folder_name = client['name'] + '/' + site['name'] + '/' + stage['name'] + '/' + session['name']
        photoscan_proceesing_folder = dir_path + '/'+ session_folder_name + "/" + 'workflow_config.json'
        cmd = common.photoscan_cmd()
        env = common.env_status()
        photoscan_response =  subprocess.check_call([cmd, photoscan_proceesing_folder, str(env)])
        print(photoscan_response)
        common.logging(photoscan_response)

        if photoscan_response == 0:
            #call publish script
            publish_metaData = {
                "api_url": api_url,
                "file_url": session_folder_name,
                "ancestor": parents
            }

            try:
                # Updating status on database for uploading photoscan
                process_name = 'UplodingFiles'

                update_process_status(process_name, site_name, stage_name, grouping)
                update_process_log(process_name, vm_details['vm_name'], vm_details)
                publish_script_params = os.path.dirname(script_path) + '/' + 'publish_files.py'
                publish_cmd = 'python3'
                param = publish_script_params + " -md '" + json.dumps(publish_metaData) + "'"
                print(param)
                publish_response = subprocess.check_call(
                    ['python3', publish_script_params, '-md', json.dumps(publish_metaData)])

                vm_details['site_name'] = site_name
                vm_details['stage_name'] = stage_name
                vm_details['grouping'] = grouping
                print('Publish response', publish_response)
                if publish_response == 0:
                    # Updating status on database for copying files to viewing vm
                    process_name = 'CopyingFilesToViewingVM'
                    update_process_status(process_name, site_name, stage_name, grouping)
                    update_process_log(process_name, vm_details['vm_name'], vm_details)
                    viewer_vm = common.viwer_vm_cred()
                    scp_file_path = common.project_path() + '/'+ session_folder_name + '/'
                    scp_target_path = common.project_path_windows() + client['name'] + '/' + site['name'] + '/' + stage['name'] + '/'
                    try:
                        scp_call = subprocess.check_call(['sshpass', '-p', viewer_vm['password'], 'scp', '-o', 'StrictHostKeyChecking=no', '-r', scp_file_path,
                                                          viewer_vm['vm_name'] + ':"' + scp_target_path + '"' ])
                        common.logging(scp_call)
                        print(scp_call)

                        #After files copied to windows viewer vm, Removing files from processing vm
                        common.remove_folder(scp_file_path)


                    except Exception as ex:
                        print('Error occured while doing scp')
                        common.logging(str(ex))
                        raise subprocess.CalledProcessError

                    publish_process_finish(publish_metaData, vm_details)

                else:
                    raise subprocess.CalledProcessError


            except Exception as ex:
                process_name = 'ErrorInProcess'
                update_process_status(process_name, site_name, stage_name, grouping)
                update_process_log(process_name, vm_details['vm_name'], vm_details)
                error = str(ex)
                common.logging(error)
                photoscan_failure_email(api_url, site_name, stage_name, grouping, process_name)

        else:
            raise subprocess.CalledProcessError

    except Exception as ex:
        process_name = 'ErrorInProcess'
        update_process_status(process_name, site_name, stage_name, grouping)
        update_process_log(process_name, vm_details['vm_name'], vm_details)
        error = str(ex)
        common.logging(error)
        photoscan_failure_email(api_url, site_name, stage_name, grouping, process_name)


def photoscan_failure_email(api_url, site_name, stage_name, grouping, process_name):
    param ={
        "emailContent" : ("Site name: %s \n Stage name: %s \n Grouping Name: %s \n Staus: %s \n Note: Please contact tech support." %(site_name, stage_name, grouping, process_name))
    }
    query = '''
            {
                photoscanFailure(input: ''' + json.dumps(json.dumps(param)) + ''') 
            }
            '''
    response = common.makeapi_call(query, api_url)
    common.logging('Photoscan failure request sent')


def find_aoi(session_id, aoi_list):
    response = {
        "status": False,
        "aoi_id": None,
        "aoi_artifacts": []
    }

    if len(aoi_list) >0:
        for aoi in aoi_list:
            aoi_data = eval(aoi['mergeReference'])

            if session_id in aoi_data:
                response["status"] = True
                response["aoi_id"] = int(aoi["id"])
                response["aoi_artifacts"] = aoi["artifacts"]
                return response

    return response

def publish_process_finish(metaData:object, vm_details):
    try:
        param = {
            'vm_name': vm_details['vm_name'],
            'vm_zone': vm_details['vm_zone'],
            'vm_id': vm_details['vm_id'],
            'site_name': vm_details['site_name'],
            'stage_name': vm_details['stage_name'],
            'grouping': vm_details['grouping'],
            'data': metaData['ancestor']
        }

        print('Final request param', param)
        common.logging('Process finish params %s' %(str(param)))
        query = '''
                    {
                              photoscanProcessFinish(input: ''' + json.dumps(json.dumps(param)) + ''') 
                    }
                    '''
        response = common.makeapi_call(query, metaData['api_url'])
        print('Final response:', response)

    except Exception as ex:
        common.logging('Error occured while finish the process')
        common.logging(str(ex))

def createDirIfNotExists(dir_name: str):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        return dir_name

def md5Checksum(filePath):
    with open(filePath, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()


def createFile(dir_path: str, file_name: str, file_url):
    if os.path.isdir(dir_path):
        return True


def downloadFileFromStorage(_file: object, fileDir: str, api_url: str):
    if os.path.isfile(fileDir + _file["fileName"]):
        if _file['fileCheckSum'] == md5Checksum(fileDir + _file["fileName"]):
            return True

    file_name = _file["name"]
    download_file_query = gql.download_file_query(file_name)
    response = common.makeapi_call(download_file_query, api_url)
    fileRequest = requests.get(response["data"]["download"]["fileUrl"])

    with open(fileDir + _file["fileName"], "wb") as artifact:
        print('Writing file :%s' % (fileDir + _file["fileName"]))
        artifact.write(fileRequest.content)
        print(fileDir + _file["fileName"] + " writing finished")
        artifact.close()
        target_file = fileDir + _file["fileName"]

        if os.path.isfile(target_file) and _file['fileName'].lower() in "photoscan.zip":
            print('Extract all the file from Photoscan.zip')
            common.make_extarctzip(target_file, fileDir)
            print('Extraction completed')


def createDirBasedJson(inputjson: object, dir_path: str, api_url: str):
    data = inputjson
    name = data["name"]
    inputType = data["type"]
    folderPath = None

    if dir_path == "":
        folderPath = name
    else:
        folderPath = dir_path + "/" + name

    if inputType == "directory":
        createDirIfNotExists(folderPath)

        # Download the workflow_config.json from storage
        # if name == "Photoscan":
        #     config_file_location = os.path.dirname(folderPath)
        #     _file = {
        #         "name" : common.work_flow_json_path(),
        #         "fileName": "workflow_config.json",
        #         "fileCheckSum": None
        #     }
        #     downloadFileFromStorage(_file, config_file_location + "/", api_url)


    if 'file' in data:
        if len(data["file"]) > 0:
            files = data["file"]
            print('files:', files)
            for _file in files:
                downloadFileFromStorage(_file, folderPath + "/", api_url)

    # inputFile = data["files"]
    children = data["children"]
    if len(children) > 0:
        for x in children:
            print(folderPath)
            createDirBasedJson(x, folderPath, api_url)


def help():
    print("Usage:- copy_files.py <options>\n" \
          "     <options> can include ->\n" \
          "     -h,--help                                   -> print this help message\n" \
          "     -md,--metadata <metadata>                   -> Metadata for copy the files\n"
          "     -site,                                      ->  site means site id\n"
          "     -stage,                                     ->  site means stage id\n"
          "     -session,                                   ->  session means session id\n"
          "     -api_url,                                   ->  api_url is workbench url\n"
          "     -vm_name,                                   ->  vm_name \n"
          "     -vm_id,                                     ->  vm_id \n"
          "     -vm_zone,                                   ->  vm_zone \n"
          "     -vm_windows,                                ->  vm_windows \n"
          "     ")


def main(argv=None):
    argv = sys.argv
    options = argv[1:]
    metadata = None
    site = None
    stage = None
    session = None
    api_url = None
    vm_name = None
    vm_id = None
    vm_zone = None
    vm_windows = False

    if (argv.count('-h') > 0) or (argv.count('--help')) > 0:
        help()
        return -1

    # For '-md,--metadata'
    if options.count('-md') > 0:
        md_idx = options.index('-md')
        if len(options[md_idx:]) < 2:
            print('Error. Specify Metadata \nCheck help with "-h"', file=sys.stdout)
            print('Error. Metadata is not specified. ', file=sys.stderr)
            sys.exit(1)
        else:
            metadata = options[md_idx + 1]
    elif options.count('--metadata') > 0:
        md_idx = options.index('--metadata')
        if len(options[md_idx:]) < 2:
            print('Error. Specify Metadata \nCheck help with "-h"', file=sys.stdout)
            print('Error. Metadata is not specified. ', file=sys.stderr)
            sys.exit(1)
        else:
            metadata = options[md_idx + 1]

    if options.count('-site') > 0:
        site_idx = options.index('-site')
        print(site_idx)
        if len(options[site_idx:]) < 0:
            print('Error. Specify Site \nCheck help with "-h"', file=sys.stdout)
            print('Error. Site is not specified. ', file=sys.stderr)
            sys.exit(1)
        else:
            site = options[site_idx + 1]
            print('site', site)

    if options.count('-stage') > 0:
        stage_idx = options.index('-stage')
        if len(options[stage_idx:]) < 1:
            print('Error. Specify Stage \nCheck help with "-h"', file=sys.stdout)
            print('Error. Stage is not specified. ', file=sys.stderr)
            sys.exit(1)
        else:
            stage = options[stage_idx + 1]
            print('stage', stage)

    if options.count('-session') > 0:
        session_idx = options.index('-session')
        if  len(options[session_idx:]) < 4:
            print('Error. Specify Session \nCheck help with "-h"', file=sys.stdout)
            print('Error. Session is not specified. ', file=sys.stderr)
            sys.exit(1)
        else:
            session = options[session_idx + 1]

    if options.count('-api_url') > 0:
        api_url_idx = options.index('-api_url')
        print(len(options[api_url_idx:]))
        if len(options[api_url_idx:]) < 2:
            print('Error. Specify  api_url\nCheck help with "-h"', file=sys.stdout)
            print('Error. api_url is not specified. ', file=sys.stderr)
            sys.exit(1)
        else:
            api_url = options[api_url_idx + 1]

    if options.count('-vm_name') > 0:
        vm_name_idx = options.index('-vm_name')
        print('vm_name', len(options[vm_name_idx:]))
        if len(options[vm_name_idx:]) < 8:
            print('Error. Specify  vm_name\nCheck help with "-h"', file=sys.stdout)
            print('Error. vm_name is not specified. ', file=sys.stderr)
            sys.exit(1)
        else:
            vm_name = options[vm_name_idx + 1]

    if options.count('-vm_id') > 0:
        vm_id_idx = options.index('-vm_id')
        print('vm_id', len(options[vm_id_idx:]))
        if len(options[vm_id_idx:]) < 6:
            print('Error. Specify  vm_id\nCheck help with "-h"', file=sys.stdout)
            print('Error. vm_id is not specified. ', file=sys.stderr)
            sys.exit(1)
        else:
            vm_id = options[vm_id_idx + 1]

    if options.count('-vm_zone') > 0:
        vm_zone_idx = options.index('-vm_zone')
        print('vm_zone', len(options[vm_zone_idx:]))
        if len(options[vm_id_idx:]) < 4:
            print('Error. Specify  vm_zone\nCheck help with "-h"', file=sys.stdout)
            print('Error. vm_zone is not specified. ', file=sys.stderr)
            sys.exit(1)
        else:
            vm_zone = options[vm_zone_idx + 1]

    if options.count('-vm_windows') > 0:
        vm_windows_idx = options.index('-vm_windows')
        print('vm_windows', len(options[vm_windows_idx:]))
        if len(options[vm_id_idx:]) < 2:
            print('Error. Specify  vm_windows\nCheck help with "-h"', file=sys.stdout)
            print('Error. vm_windows is not specified. ', file=sys.stderr)
            sys.exit(1)
        else:
            vm_windows = options[vm_windows_idx + 1]

    if site is None or stage is None or session is None :
        print('ERROR 1. Site or Stage or Session is missed.', file=sys.stdout)
        print('ERROR 1. Site or Stage or Session is missed.', file=sys.stderr)
    else:
        data = {
            'Site': site,
            'Stage': stage,
            'Session': session
        }
        vm_details = {
            'vm_name': vm_name,
            'vm_zone': vm_zone,
            'vm_id': vm_id
        }

        copy_files(data, api_url, vm_details, vm_windows)


def session_list_artifacts(artifcat_list):
    ref = []
    images_folder = folder['images']
    input_folder = folder['input']
    input_files = []
    image_files = []
    session_files = []
    files = artifcat_list
    for _file in files:
        raw_file = {}
        raw_file['id'] = _file['id']
        raw_file['name'] = _file['name']
        raw_file['fileName'] = _file['fileName']
        raw_file['fileCheckSum'] = _file['fileCheckSum']

        if _file['type'] == 'raw':
            image_files.append(raw_file)
        elif _file['type'] == 'gcp':
            input_files.append(raw_file)
        elif _file['type'] == 'workflow_config':
            session_files.append(raw_file)

    images_folder['file'] = image_files
    input_folder['file'] = input_files
    ref.append(input_folder)
    ref.append(images_folder)
    response = {
        "children": ref, "session_files": session_files
    }

    return response

def aoi_list_artifacts(artifcat_list):
    ref = []
    output_folder = folder['output']
    photoscan_folder = folder['photoscan']
    project_reports_folder = folder['project_reports']
    workspace_folder = folder['workspace']
    files = artifcat_list
    exec_rep_files = []
    psrep_files = []
    output_files = []
    photoscan_files = []

    for _file in files:
        raw_file = {}
        raw_file['id'] = _file['id']
        raw_file['name'] = _file['name']
        raw_file['fileName'] = _file['fileName']
        raw_file['fileCheckSum'] = _file['fileCheckSum']

        if _file['type'] == 'dem':
            output_files.append(raw_file)
        elif _file['type'] == 'mosaic':
            output_files.append(raw_file)
        elif _file['type'] == 'dsm':
            output_files.append(raw_file)
        elif _file['type'] == 'dtm':
            output_files.append(raw_file)
        elif _file['type'] == 'contour':
            output_files.append(raw_file)
        elif _file['type'] == 'mosaic':
            output_files.append(raw_file)
        elif _file['type'] == 'execrep':
            exec_rep_files.append(raw_file)
        elif _file['type'] == 'psrep':
            psrep_files.append(raw_file)
        elif _file['type'] == 'photoscan':
            photoscan_files.append(raw_file)

    output_folder['file'] = output_files

    for project_report in project_reports_folder['children']:
        if project_report['name'] is "Photoscan Reports":
            # Photoscan report files append to project report
            project_report['file'].append(psrep_files)

        elif project_report['name'] is "Execution Reports":
            # Execution report files append to project report
            project_report['file'].append(exec_rep_files)

    ref.append(output_folder)
    ref.append(photoscan_folder)
    ref.append(project_reports_folder)
    ref.append(workspace_folder)
    response = {
        "children": ref, "photoscan_files": photoscan_files
    }

    return response


if __name__ == "__main__":
    sys.exit(main())