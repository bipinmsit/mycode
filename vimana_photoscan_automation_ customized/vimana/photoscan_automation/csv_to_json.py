import csv
import json
import os
import ntpath
ntpath.basename("a/b/c")

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def merge(a, b, path=None):
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


def csv_to_json(path_to_csv=os.path.realpath(__file__)):
    input_file = csv.DictReader(open(path_to_csv))
    parameter_list = list(input_file)
    number_of_experiments = len(parameter_list)
    i = 0
    while i < number_of_experiments:
        keys = list(parameter_list[i].keys())
        for row in keys:
            csv_file_name = os.path.splitext(path_leaf(path_to_csv))[0]
            workflow_file = os.path.join(os.path.dirname(os.path.realpath(path_to_csv))) +"/"+ csv_file_name +"_"+ str(i+1) + ".json"
            params_list = row.split('-')
            step = params_list[0]

            dict_from_param_list = {step: {}}

            params = params_list[1]

            value = parameter_list[i][row]
            if len(params_list) > 2:
                sub_params = params_list[2]
                dict_from_param_list[step][params] = {}
                dict_from_param_list[step][params][sub_params] = value
            else:
                dict_from_param_list[step][params] = value

            if os.path.isfile(workflow_file):
                wf = open(workflow_file, 'r')
                final_json = json.load(wf)
                dict_from_param_list = merge(dict_from_param_list, final_json)

            with open(workflow_file, 'w') as outfile:
                json.dump(dict_from_param_list, outfile, indent=10)
        i = i + 1


if __name__ == "__main__":
    # add the path to the csv file
    csv_to_json("/home/aspecscire/Desktop/vimana-photoscan-automation/vimana/photoscan_automation/experiment1_dense_cloud_quality.csv")
