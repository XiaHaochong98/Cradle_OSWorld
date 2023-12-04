import re
import ast
import time
from typing import Dict, Any
import inspect

from uac.config import Config

config = Config()
SKILL_REGISTRY = {}


def register_skill(name):
    def decorator(skill):
        SKILL_REGISTRY[name] = skill
        return skill
    return decorator


def extract_function_info(input_string: str = "open_map()"):

    pattern = re.compile(r'(\w+)\((.*?)\)')

    match = pattern.match(input_string)

    if match:
        function_name = match.group(1)
        raw_arguments = match.group(2)

        try:
            parsed_arguments = ast.parse(f"fake_func({raw_arguments})", mode='eval')
        except SyntaxError:
            raise ValueError("Invalid function call/arg format to parse.")

        arguments = {}
        for node in ast.walk(parsed_arguments):
            if isinstance(node, ast.keyword):
                arguments[node.arg] = ast.literal_eval(node.value)

        if len(raw_arguments) > 0 and len(arguments.keys()) == 0:
            raise ValueError("Call arguments not properly parsed!")

        return function_name, arguments
    else:
        raise ValueError("Invalid function call format string.")


def execute_skill(name: str = "open_map", params: Dict = None):
    if name in SKILL_REGISTRY:
        skill = SKILL_REGISTRY[name]
        skill(**params)
    else:
        raise ValueError(f"Function '{name}' not found in the registry.")


def convert_expression_to_skill(expression: str = "open_map()"):
    skill_name, skill_params = extract_function_info(expression)
    return skill_name, skill_params


def get_skill_library(skill: Any) -> Dict:
    docstring = inspect.getdoc(skill)

    if docstring:

        params = inspect.signature(skill).parameters

        if len(params) > 0:
            param_descriptions = {}
            for param in params.values():
                name = param.name
                param_description = re.search(rf"- {name}: (.+).", docstring).group(1)
                param_descriptions[name] = param_description
            return {
                "function_expression": f"{skill.__name__}({', '.join(params.keys())})",
                "description": docstring,
                "parameters": param_descriptions,
            }
        else:
            return {
                "function_expression": f"{skill.__name__}()",
                "description": docstring,
                "parameters": {},
            }
    else:
        return None


def get_skill_library_in_code(skill: Any) -> str:
    return inspect.getsource(skill)


def post_skill_wait(wait_time: config.DEFAULT_POST_ACTION_WAIT_TIME):
    """Wait for skill to finish. Like if there is an animation"""
    time.sleep(wait_time)