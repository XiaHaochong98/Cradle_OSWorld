import os
import sys
import argparse
import time
import json

from uac.agent import Agent
from uac.agent.agent import to_text
from uac.config import Config
from uac.gameio import GameManager
from uac.planner.planner import Planner
from uac.log import Logger
from uac.provider.openai import OpenAIProvider, encode_image
from uac.utils.file_utils import assemble_project_path, read_resource_file


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
    base64_image = encode_image(image)

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
    gm = GameManager(config.env_name)

    # Creating planner, which encapsulates model use

    planner_params = {
        "__check_list__":[
            "gather_information"
        ],
        "prompt_paths": {
            "input_example": {
            "gather_information": "./res/prompts/input_example/gather_information.json",
            "decision_making": "./res/prompts/input_example/decision_making.json",
            "success_detection": "./res/prompts/input_example/success_detection_frl.json",
            },
            "template": {
            "gather_information": "./res/prompts/templates/describe_image.prompt",
            "decision_making": "./res/prompts/templates/decision_making.prompt",
            "success_detection": "./res/prompts/templates/success_detection.prompt",
            },
            "output_example": {
            "gather_information": "./res/prompts/output_example/gather_information.json",
            "decision_making": "./res/prompts/output_example/decision_making.json",
            "success_detection": "./res/prompts/output_example/success_detection.json",
            }
        }
    }

    system_prompt_template = read_resource_file("./res/prompts/templates/system.prompt")
    args = {"environment_name" : config.env_name}
    system_prompt = to_text(system_prompt_template, args)

    planner = Planner(provider, [system_prompt], planner_params)

    # result_str = planner._gather_information(screenshot_file=rel_image)
    # result = json.loads(result_str)["description"]

    # Creating agent with its dependencies
    agent = Agent("TestAgent", None, gm, planner)
    agent.loop()

    logger.write()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--providerConfig",
        type=str,
        default=None,
    )

    args = parser.parse_args()

    main(args)