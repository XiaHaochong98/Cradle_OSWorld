import re
import ast
import time
from typing import Dict, Any, List
import inspect
import numpy as np
import copy
import os
import base64

from uac.config import Config
from uac.utils.json_utils import load_json, save_json
import pydirectinput
import pyautogui

config = Config()
SKILL_REGISTRY = {}
SKILL_INDEX = []

SKILL_NAME_KEY = 'skill_name'
SKILL_DOCUMENTATION_KEY = 'skill_doc'
SKILL_EMBEDDING_KEY = 'skill_emb'
SKILL_CODE_KEY = 'skill_code'
SKILL_DOC_HASH_KEY = 'skill_doc_base64'


def register_skill(name):
    def decorator(skill):
        SKILL_REGISTRY[name] = skill
        SKILL_INDEX.append({SKILL_NAME_KEY:          name,
                            SKILL_DOCUMENTATION_KEY: inspect.getdoc(skill),
                            SKILL_EMBEDDING_KEY:     None,
                            SKILL_CODE_KEY:          inspect.getsource(skill)})
        return skill
    return decorator


def post_skill_wait(wait_time: config.DEFAULT_POST_ACTION_WAIT_TIME):
    """Wait for skill to finish. Like if there is an animation"""
    time.sleep(wait_time)


class SkillRegistry:

    skill_library_filename = 'skill_lib.json'

    def __init__(
        self,
        local_path = '',
        from_local = False,
        store_path = '',
        embedding_provider = None
    ):
        self.from_local = from_local
        self.local_path = local_path
        self.store_path = store_path
        self.embedding_provider = embedding_provider
        self.recent_skills = []
        self.necessary_skills = []
        
        if self.from_local:
            # @TODO validate the local skill registry exists
            self.load_skill_library()
        else:
            self.skill_registry = copy.deepcopy(SKILL_REGISTRY)
            self.skill_index = copy.deepcopy(SKILL_INDEX)
            for skill in self.skill_index:
                skill[SKILL_EMBEDDING_KEY] = self.get_embedding(skill[SKILL_NAME_KEY], inspect.getdoc(SKILL_REGISTRY[skill[SKILL_NAME_KEY]]))


    def extract_function_info(self, input_string: str = "open_map()"):

        pattern = re.compile(r'(\w+)\((.*?)\)')

        match = pattern.match(input_string)

        if match:
            function_name = match.group(1)
            raw_arguments = match.group(2)

            # To avoid simple errors based on faulty model output
            if raw_arguments is not None and len(raw_arguments) > 0:
                raw_arguments = raw_arguments.replace("=false", "=False").replace("=true", "=True")

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


    def execute_skill(self, name: str = "open_map", params: Dict = None):

        # @TODO return execution error info

        if name in self.skill_registry:
            skill = self.skill_registry[name]
            skill(**params)
        else:
            raise ValueError(f"Function '{name}' not found in the registry.")


    def convert_expression_to_skill(self, expression: str = "open_map()"):
        skill_name, skill_params = self.extract_function_info(expression)
        return skill_name, skill_params


    def get_from_skill_library(self, skill_name: str) -> Dict:
        skill = self.skill_registry[skill_name]
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


    def get_skill_library_in_code(self, skill: Any) -> str:
        return inspect.getsource(skill)


    def register_skill_from_code(self, skill_code: str, skill_doc: str) -> None:

        def get_func_name(skill_code):
            return skill_code.split('def ')[-1].split('(')[0]
        
        skill_name = get_func_name(skill_code)
        if skill_name not in self.skill_registry:
            exec(skill_code)
            skill = eval(skill_name)
            skill.__doc__ = skill_doc
            self.skill_registry[skill_name] = skill
            self.skill_index.append({SKILL_NAME_KEY:          skill_name,
                                    SKILL_DOCUMENTATION_KEY: skill_doc,
                                    SKILL_EMBEDDING_KEY:     self.get_embedding(skill_name, skill_doc),
                                    SKILL_CODE_KEY:          skill_code})
            self.recent_skills.append(skill_name)
        else:
            if skill_name not in self.recent_skills:
                self.recent_skills.append(skill_name)


    def retrieve_skills(self, query_task: str, skill_num: int) -> List[str]:
        skill_num = min(skill_num, len(self.skill_index))
        target_skills = [skill for skill in self.recent_skills] + [skill for skill in self.necessary_skills]
        task_emb = np.array(self.embedding_provider.embed_query(query_task))
        self.skill_index.sort(key = lambda x: -np.dot(x[SKILL_EMBEDDING_KEY],task_emb))
        for skill in self.skill_index:
            if len(target_skills)>=skill_num:
                break
            else:
                if skill[SKILL_NAME_KEY] not in target_skills:
                    target_skills.append(skill[SKILL_NAME_KEY])
        self.recent_skills = []
        return target_skills
    
    def register_available_skills(self, candidates:List[str]) -> None:
        for skill_key in list(self.skill_registry.keys()):
            if skill_key not in candidates:
                del self.skill_registry[skill_key]
        self.skill_index_t = []
        for skill in self.skill_index:
            if skill[SKILL_NAME_KEY] in candidates:
                self.skill_index_t.append(skill)
        self.skill_index = copy.deepcopy(self.skill_index_t)
        del self.skill_index_t


    def get_all_skills(self) -> List[str]:
        return list(self.skill_registry.keys())


    def get_embedding(self, skill_name, skill_doc):
        return np.array(self.embedding_provider.embed_query('{}: {}'.format(skill_name, skill_doc)))
        #return np.array(self.embedding_provider.embed_query(skill_doc))


    def convert_str_to_func(self, skill_name, skill_local):
        exec(skill_local[skill_name][SKILL_CODE_KEY])
        skill = eval(skill_name)
        skill.__doc__ = skill_local[skill_name][SKILL_DOCUMENTATION_KEY]
        return skill


    def store_skills(self) -> None:
        store_file = {}
        for skill in self.skill_index:
            store_file[skill[SKILL_NAME_KEY]] = {SKILL_DOCUMENTATION_KEY:skill[SKILL_DOCUMENTATION_KEY],
                                                 SKILL_CODE_KEY:skill[SKILL_CODE_KEY],
                                                 SKILL_EMBEDDING_KEY:base64.b64encode(skill[SKILL_EMBEDDING_KEY].tobytes()).decode('utf-8'),
                                                 SKILL_DOC_HASH_KEY:base64.b64encode(skill[SKILL_DOCUMENTATION_KEY].encode('utf-8')).decode('utf-8')}

        save_json(file_path = os.path.join(self.store_path, self.skill_library_filename), json_dict = store_file, indent = 4)


    def load_skill_library(self) -> None:

        skill_local = load_json(os.path.join(self.local_path, self.skill_library_filename))

        self.skill_index = []
        self.skill_registry = {}

        for skill_name in skill_local.keys():

            if skill_name in SKILL_REGISTRY:
                # the manually-designed skills follow the code in .py files
                self.skill_registry[skill_name] = SKILL_REGISTRY[skill_name]

                skill_doc_base64 = base64.b64encode(skill_local[skill_name][SKILL_DOCUMENTATION_KEY].encode('utf-8')).decode('utf-8')

                if skill_doc_base64 == skill_local[skill_name][SKILL_DOC_HASH_KEY]: # the skill_doc is not modified
                    self.skill_index.append({SKILL_NAME_KEY:skill_name,
                                             SKILL_DOCUMENTATION_KEY:inspect.getdoc(SKILL_REGISTRY[skill_name]),
                                             SKILL_EMBEDDING_KEY:np.frombuffer(base64.b64decode(skill_local[skill_name][SKILL_EMBEDDING_KEY]), dtype=np.float64),
                                             SKILL_CODE_KEY:inspect.getsource(SKILL_REGISTRY[skill_name])})

                else: # skill_doc has been modified, we should recompute embeddings
                    self.skill_index.append({SKILL_NAME_KEY:skill_name,
                                             SKILL_DOCUMENTATION_KEY:inspect.getdoc(SKILL_REGISTRY[skill_name]),
                                             SKILL_EMBEDDING_KEY:self.get_embedding(skill_name, inspect.getdoc(SKILL_REGISTRY[skill_name])),
                                             SKILL_CODE_KEY:inspect.getsource(SKILL_REGISTRY[skill_name])})

            else:
                # the skills got from gather_information follow the code in .json file
                skill = self.convert_str_to_func(skill_name, skill_local)
                self.skill_registry[skill_name] = skill

                skill_doc_base64 = base64.b64encode(skill_local[skill_name][SKILL_DOCUMENTATION_KEY].encode('utf-8')).decode('utf-8')

                if skill_doc_base64 == skill_local[skill_name][SKILL_DOC_HASH_KEY]: # the skill_doc is not modified
                    self.skill_index.append({SKILL_NAME_KEY:skill_name,
                                             SKILL_DOCUMENTATION_KEY:inspect.getdoc(skill),
                                             SKILL_EMBEDDING_KEY:np.frombuffer(base64.b64decode(skill_local[skill_name][SKILL_EMBEDDING_KEY]), dtype=np.float64),
                                             SKILL_CODE_KEY:skill_local[skill_name][SKILL_CODE_KEY]})

                else: # skill_doc has been modified, we should recompute embedding
                    self.skill_index.append({SKILL_NAME_KEY:skill_name,
                                             SKILL_DOCUMENTATION_KEY:inspect.getdoc(skill),
                                             SKILL_EMBEDDING_KEY:self.get_embedding(skill_name, inspect.getdoc(skill)),
                                             SKILL_CODE_KEY:skill_local[skill_name][SKILL_CODE_KEY]})
