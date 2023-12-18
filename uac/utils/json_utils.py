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


# def refine_json(json_string):
#     if not check_json(json_string):
#         json_string = json_string.replace("```json\n", "").replace("json```\n", "").replace("```", "").replace("\r\n", "").replace("\n", "").replace("\'", "")

#     trailing_comma_pattern = r",(\s*)([}\]])"
#     replacement_pattern = r"\1\2"  # Keeps the captured whitespaces group
#     json_string = re.sub(trailing_comma_pattern, replacement_pattern, json_string)

#     return json_string

# def refine_json(json_string):
#     if not check_json(json_string):
#         pattern = r"^`+json(.*?)`+"
#         match = re.search(pattern, json_string, re.DOTALL)
#         if match:
#             json_string = match.group(1)
#     return json_string

def refine_json(json_string):
    patterns = [
        r"^`+json(.*?)`+", # ```json content```, ```json content``, ...
        r"^json(.*?)", # json content
        r"^json(.*?)\." # json content.
    ]

    for pattern in patterns:
        match = re.search(pattern, json_string, re.DOTALL)
        if match:
            json_string = match.group(1)
            if check_json(json_string):
                return json_string
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

def parse_semi_formatted_text(text):
    lines = text.split('\n')
    result_dict = {}

    current_key = None
    current_value = []

    for line in lines:
        if line.endswith(":"):
            current_key = line.rstrip(':')
            current_value = []
        else:
            current_value.append(line)

        result_dict[current_key.lower()] = '\n'.join(current_value).strip()

    if "actions" in result_dict:
        actions = result_dict["actions"]
        actions = actions.replace('```python', '').replace('```', '')
        actions = actions.split('\n')
        actions = [action for action in actions if action]

        actions = [action.split('#')[0].strip() for action in actions if "#" in action]

        result_dict["actions"] = actions

    if "success" in result_dict:
        result_dict["success"] = result_dict["success"].lower() == "true"

    return result_dict
