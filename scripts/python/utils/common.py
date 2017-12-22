# Common

import json, sys, os
import hashlib
import zipfile
import requests
import time
import shutil

script_path = os.path.realpath(__file__)
python_path = os.path.dirname(script_path)
sys.path.append(python_path)

class Common():
    config = json.load(open(python_path + '/config/config.json'))
    env = config['env']
    common_config = None
    if env == True :
        common_config = config["prodConfig"]
    else:
        common_config = config["testConfig"]


    def work_flow_json_path(self):
        work_flow_json = self.config['work_flow_json']
        return work_flow_json

    def mapbox_api_credentials(self):
        data = { 'credentials': self.config['mapbox_credentials'], 'apiUrl': self.config['apiUrl']}
        return data

    def viwer_vm_cred(self):
        viewer_vm = self.common_config['viewer_vm']
        data = {
            "vm_name" : viewer_vm['vm_name'],
            "password" : viewer_vm['password']
        }

        return data

    def mysql_conn(self):
        return self.common_config['mysql']

    def env_status(self):
        return  self.env

    def api_url(self):
        return  self.config['apiUrl']

    def project_path(self):
        return self.config['projectFolderPath']

    def project_path_windows(self):
        return self.config['projectFolderPathWindows']

    def photoscan_cmd(self):
        return self.config['photoscanCmd']

    def logging(self, exception):
        script_path = os.path.realpath(__file__)
        python_path = os.path.dirname(script_path)

        if not os.path.isfile(python_path + '/' + 'python_log.txt'):
            with(open(python_path + '/' + 'python_log.txt', 'w')) as log:
                log.write('----Log File created at: %s ---- \n' % (time.strftime('%c')))
                log.close()

        with(open(python_path + '/' + 'python_log.txt', 'a')) as log:
            log.write('----Created at: %s ---- \n' % (time.strftime('%c')))
            log.write(str(exception) + '\n')
            log.write('----Finished at: %s ---- \n' % (time.strftime('%c')))
            log.close()

    def zip_files(self, folder_path, target_file):
        zf = zipfile.ZipFile(target_file, "w")
        for dirname, subdirs, files in os.walk(folder_path):
            zf.write(dirname)
            for filename in files:
                zf.write(os.path.join(dirname, filename))
        zf.close()

    def zip_folder(self, folder_path, output_path):
        """Zip the contents of an entire folder (with that folder included
        in the archive). Empty subfolders will be included in the archive
        as well.
        """
        print(folder_path)
        print(output_path)
        parent_folder = os.path.dirname(folder_path)
        # Retrieve the paths of the folder contents.
        contents = os.walk(folder_path)
        try:
            zip_file = zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED)
            for root, folders, files in contents:
                # Include all subfolders, including empty ones.
                for folder_name in folders:
                    absolute_path = os.path.join(root, folder_name)
                    relative_path = absolute_path.replace(parent_folder + '\\',
                                                          '')
                    print("Adding '%s' to archive." % (absolute_path))
                    zip_file.write(absolute_path, relative_path)
                for file_name in files:
                    absolute_path = os.path.join(root, file_name)
                    relative_path = absolute_path.replace(parent_folder + '\\',
                                                          '')
                    print("Adding '%s' to archive." % (absolute_path))
                    zip_file.write(absolute_path, relative_path)
            print("'%s' created successfully." % (output_path))
        except IOError as message :
            print(message)
            sys.exit(1)
        except OSError as message:
            print(message)
            sys.exit(1)
        except zipfile.BadZipfile as message:
            print(message)
            sys.exit(1)
        finally:
            zip_file.close()



    def md5Checksum(filePath):
        with open(filePath, 'rb') as fh:
            m = hashlib.md5()
            while True:
                data = fh.read(8192)
                if not data:
                    break
                m.update(data)
            return m.hexdigest()

    def make_zipfile(self, output_filename, source_dir):
        relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
        with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip:
            for root, dirs, files in os.walk(source_dir):
                # add directory (needed for empty dirs)
                zip.write(root, os.path.relpath(root, relroot))
                for file in files:
                    filename = os.path.join(root, file)
                    if os.path.isfile(filename):  # regular files only
                        arcname = os.path.join(os.path.relpath(root, relroot), file)
                        zip.write(filename, arcname)

    def make_extarctzip(self, zip_file, target_dir):
        zip_ref = zipfile.ZipFile(zip_file, 'r')
        zip_ref.extractall(target_dir)
        zip_ref.close()

    def makeapi_call(self, query, api_url):
        response = requests.get(api_url+ query)
        return response.json()

    def download_file_content(self, api_url):
        file_request = requests.get(api_url)
        return file_request.content

    def remove_folder(self, folder_path:str):
        if os.path.exists(folder_path):
            try:
                self.logging('Starting remove folder, Folder name : %s' %(folder_path))
                shutil.rmtree(folder_path)
                return True
            except Exception as ex:
                self.logging('Error occured while removing folder, Folder Name : %s' %(folder_path))
                self.logging(str(ex))
                return False
        else:
            return False




if __name__  == '__main__':
    common = Common()



