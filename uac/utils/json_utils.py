import json


def load_json(file_path):
    with open(file_path, mode='r', encoding='utf8') as fp:
        json_dict = json.load(fp)
        return json_dict
    
def save_json(file_path, json_dict, indent=-1):
    with open(file_path, mode='w', encoding='utf8') as fp:
        if indent == -1:
            json.dump(json_dict, fp, ensure_ascii=False)
        else:
            json.dump(json_dict, fp, ensure_ascii=False, indent=indent)


def check_json(json_string):
    try:
        json.loads(json_string)
    except:
        return False
    return True


def refine_json(json_string):
    if not check_json(json_string):
        json_string = json_string.replace("```json\n", "").replace("json```\n", "").replace("```", "").replace("\n", "").replace("\'", "")
    return json_string            


def parse_semi_formatted_json(json_string):

    response = refine_json(json_string)
    obj = json.loads(response)

    return obj