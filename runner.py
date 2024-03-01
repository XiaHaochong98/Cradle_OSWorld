import os
import sys
import argparse
import time
import json

from uac.agent import Agent
from uac.config import Config
from uac.gameio import GameManager
from uac.planner.planner import Planner
from uac.log import Logger
from uac.provider.openai import OpenAIProvider, encode_image_path
from uac.utils.file_utils import assemble_project_path, read_resource_file
from uac.memory import LocalMemory
from uac.gameio.skill_registry import SkillRegistry


def main(args):

    config = Config()
    logger = Logger()

    # Create provider and make simple calls
    provider = OpenAIProvider()
    provider.init_provider(args.providerConfig) # config passed in from command line argument
                                                # in vscode, there is already an example ready to run, no need to pass parameters here

    # sample call to get an embedding
    # res_emb = provider.embed_query("Hello world")

    # sample call to get a completion from messages with text and image

    rel_image = "./res/samples/game_screenshot.jpg"
    image = assemble_project_path(rel_image)
    base64_image = encode_image_path(image)

    prompt_messages=[
        {"role": "system", "content": [
            {"type" : "text", "text" : "Act like an agent to interpret my commands."}
        ]},
        {"role": "user", "content": [
            {"type": "text", "text": "Who are you and what is your version? Are you GPT-4V? Can I send you an image?"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]}
    ]

    # res_comp = provider.create_completion(prompt_messages)
    # response = res_comp[0]

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
                "decision_making": "./res/prompts/inputs/decision_making.json",
                "gather_information": "./res/prompts/inputs/gather_information.json",
                "success_detection": "./res/prompts/inputs/success_detection.json",
                "information_summary": "./res/prompts/inputs/information_summary.json",
                "gather_text_information": "./res/prompts/inputs/gather_text_information.json",
            },
            "templates": {
                "decision_making": "./res/prompts/templates/decision_making.prompt",
                "gather_information": "./res/prompts/templates/gather_information.prompt",
                "success_detection": "./res/prompts/templates/success_detection.prompt",
                "information_summary": "./res/prompts/templates/information_summary.prompt",
                "gather_text_information": "./res/prompts/templates/gather_text_information.prompt",
            },
        }
    }

    planner = Planner(llm_provider=provider, planner_params=planner_params, use_screen_classification = False, use_information_summary= False)

    # result_str = planner._gather_information(screenshot_file=rel_image)
    # result = json.loads(result_str)["description"]

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

    # parser.add_argument(
    #     '--no_continuous',
    #     action=argparse.BooleanOptionalAction
    # )

    args = parser.parse_args()

    main(args)
