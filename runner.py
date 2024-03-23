import argparse

from cradle.agent import Agent
from cradle.config import Config
from cradle.gameio import GameManager
from cradle.planner.planner import Planner
from cradle.log import Logger
from cradle.provider.openai import OpenAIProvider, encode_image_path
from cradle.utils.file_utils import assemble_project_path, read_resource_file
from cradle.memory import LocalMemory
from cradle.environment.rdr2.skill_registry import SkillRegistry


def main(args):

    config = Config()
    logger = Logger()

    # Create provider and make simple calls
    provider = OpenAIProvider()
    provider.init_provider(args.providerConfig) # config passed in from command line argument
                                                # in vscode, there is already an example ready to run, no need to pass parameters here

    # Creating game manager to interact with game
    gm = GameManager(env_name = config.env_name,
                     embedding_provider = provider)

    # Creating memory to store recent historical information
    memory = LocalMemory(memory_path=config.work_dir,
                         max_recent_steps=config.max_recent_steps)

    # Creating planner, which encapsulates model use

    planner_params = {
        "__check_list__": [
            "decision_making",
            "gather_information",
            "success_detection",
            "information_summary",
            "gather_text_information",
        ],
        "prompt_paths": {
            "inputs": {
                "decision_making": "./res/prompts/inputs/rdr2/decision_making.json",
                "gather_information": "./res/prompts/inputs/rdr2/gather_information.json",
                "success_detection": "./res/prompts/inputs/rdr2/success_detection.json",
                "information_summary": "./res/prompts/inputs/rdr2/information_summary.json",
                "gather_text_information": "./res/prompts/inputs/rdr2/gather_text_information.json",
            },
            "templates": {
                "decision_making": "./res/prompts/templates/rdr2/decision_making.prompt",
                "gather_information": "./res/prompts/templates/rdr2/gather_information.prompt",
                "success_detection": "./res/prompts/templates/rdr2/success_detection.prompt",
                "information_summary": "./res/prompts/templates/rdr2/information_summary.prompt",
                "gather_text_information": "./res/prompts/templates/rdr2/gather_text_information.prompt",
            },
        }
    }

    planner = Planner(llm_provider=provider, planner_params=planner_params, use_screen_classification = False, use_information_summary= False)

    # Creating agent with its dependencies
    agent = Agent("UAC Agent", memory, gm, planner)
    agent.loop()

    logger.write()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--providerConfig",
        type=str,
        default="./conf/openai_config.json",
    )

    parser.add_argument(
        "--envConfig",
        type=str,
        default="./conf/env_config_rdr2.json",
    )

    # parser.add_argument(
    #     '--no_continuous',
    #     action=argparse.BooleanOptionalAction
    # )

    args = parser.parse_args()

    main(args)
