import requests

# in seconds
REQUEST_TIMEOUT = 5


class AgentClient:

    def __init__(self, base_url):
        self.base_url = base_url
    
    def execute_task(self, command, args=[], options={}):
        post_data = {
            "type": command,
            "args": args,
            "options": options
        }
        response = requests.post(self.base_url, json=post_data, timeout=REQUEST_TIMEOUT)
        if response.status_code == 204:
            print("Task successfully started on VM")
            return response.status_code
        else:
            raise Exception("Could not start requested Task on VM")

    def get_status(self):
        """
        Returns Status: idle, running, finished, error
        :return:
        """
        response = requests.get('{}/status'.format(self.base_url), timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception("Unexpected Response while getting Status from VM")

    def get_log(self):
        """
        Returns recent Logs
        :return:
        """
        response = requests.get('{}/log'.format(self.base_url), timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception("Unexpected Response While fetching Log from VM")
