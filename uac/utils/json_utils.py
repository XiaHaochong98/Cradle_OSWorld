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

    lines = [line.rstrip() for line in lines if line.rstrip()]
    result_dict = {}
    current_key = None
    current_value = []
    parsed_data = []
    in_code_flag = False

    for line in lines:
        # Check if the line indicates a new key
        if line.endswith(":") and in_code_flag == False:
            # If there's a previous key, process its values
            if current_key and current_key.lower() == "context-sensitive prompts":
                result_dict[current_key.lower()] = parsed_data
            elif current_key:
                result_dict[current_key.lower()] = '\n'.join(current_value).strip()

            current_key = line.rstrip(':')
            current_value = []
            parsed_data = []
        else:
            if current_key.lower() == "context-sensitive prompts":
                in_code_flag = True
                if line.strip() == '```':
                    if current_value:  # Process previous code block and description
                        entry = {"code": '\n'.join(current_value[1:])}
                        parsed_data.append(entry)
                        current_value = []
                    in_code_flag = False
                else:
                    current_value.append(line)
            else:
                in_code_flag = False
                line = line.strip()
                current_value.append(line)

    # Process the last key
    if current_key.lower() == "context-sensitive prompts":
        if current_value:  # Process the last code block and description
            entry = {"code": '\n'.join(current_value[:-1]).strip()}
            parsed_data.append(entry)
        result_dict[current_key.lower()] = parsed_data
    else:
        result_dict[current_key.lower()] = '\n'.join(current_value).strip()

    if "actions" in result_dict:
        actions = result_dict["actions"]
        actions = actions.replace('```python', '').replace('```', '')
        actions = actions.split('\n')

        actions = [action for action in actions if action]

        actions = [action.split('#')[0] if "#" in action else action for action in actions]

        result_dict["actions"] = actions

    if "success" in result_dict:
        result_dict["success"] = result_dict["success"].lower() == "true"

    return result_dict
