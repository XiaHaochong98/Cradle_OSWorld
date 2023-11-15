import os
import sys
import argparse
import time

from uac.agent import Agent
from uac.config import Config
from uac.provider.openai import OpenAIProvider, encode_image


def main(args):

    config = Config()

    # create provider and make simple calls
    provider = OpenAIProvider()
    provider.init_provider(args.providerConfig) # config passed in from command line argument
                                                # in vscode, there is already an example ready to run, no need to pass parameters here   

    # sample call to get an embedding
    res_emb = provider.embed_query("Hello world")

    # sample call to get a completion from messages with text and image

    image = "./res/samples/game_screenshot.jpg"
    if not os.path.isabs(image):
        image = os.path.join(config.work_dir, image)

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

    res_comp = provider.create_completion(prompt_messages)
    response = res_comp[0]

    # sample creating dummy agent
    #agent = Agent("TestAgent", None, provider)
    #agent.loop()

    print()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--providerConfig",
        type=str,
        default=None,
    )

    args = parser.parse_args()

    main(args)