import json
import re

from uac.log import Logger

logger = Logger()


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
        json_string = json_string.replace("```json\n", "").replace("json```\n", "").replace("```", "").replace("\r\n", "").replace("\n", "").replace("\'", "")

    trailing_comma_pattern = r",(\s*)([}\]])"
    replacement_pattern = r"\1\2"  # Keeps the captured whitespaces group
    json_string = re.sub(trailing_comma_pattern, replacement_pattern, json_string)

    return json_string


def parse_semi_formatted_json(json_string):

    obj = None

    try:
        response = refine_json(json_string)
        obj = json.loads(response)

    except Exception as e:
        logger.error(f"Error in processing json: {e}. Object was: {json_string}.")
        logger.error_ex(e)

    return obj
