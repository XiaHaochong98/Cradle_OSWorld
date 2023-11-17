import os
from typing import Dict

from uac.config import Config
from uac.log import Logger

cfg = Config()
logger = Logger()

def check_planner_params(planner: Dict = None):

    flag = True

    try:
        # check keys
        assert "prompt_paths" in planner, f"prompt_paths is not in planner"
        assert "__check_list__" in planner, f"__check_list__ is not in planner"

        prompt_paths = planner["prompt_paths"]
        assert "input_example" in prompt_paths, f"input_example is not in prompt_paths"
        assert "template" in prompt_paths, f"template is not in prompt_paths"
        assert "output_example" in prompt_paths, f"output_example is not in prompt_paths"

        input_example = prompt_paths["input_example"]
        template = prompt_paths["template"]
        output_example = prompt_paths["output_example"]

        """check modules"""
        check_list = planner["__check_list__"]
        for check_item in check_list:
            assert (check_item in input_example and
                    os.path.exists(os.path.join(cfg.work_dir, input_example[check_item]))), \
                f"{check_item} is not in input_example or {os.path.join(cfg.work_dir, input_example[check_item])} does not exist"
            assert (check_item in template and
                    os.path.exists(os.path.join(cfg.work_dir, template[check_item]))), \
                f"{check_item} is not in template or {os.path.join(cfg.work_dir, template[check_item])} does not exist"
            assert (check_item in output_example and
                    os.path.exists(os.path.join(cfg.work_dir, output_example[check_item]))), \
                f"{check_item} is not in output_example or {os.path.join(cfg.work_dir, output_example[check_item])} does not exist"

    except Exception as e:
        logger.error(f"Error in check_prompt_paths: {e}")
        flag = False

    return flag