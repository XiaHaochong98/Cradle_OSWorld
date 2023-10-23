import json


def load_json(file_path):
    with open(file_path, mode='r') as fp:
        json_dict = json.load(fp)
        return json_dict
    
def save_json(file_path, json_dict, indent=-1):
    with open(file_path, mode='w') as fp:
        if indent == -1:
            json.dump(json_dict, fp)
        else:
            json.dump(json_dict, fp, indent=indent)
