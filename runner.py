import os
import sys
import argparse
import time

from uac.agent import Agent
from uac.config import Config
from uac.provider.openai import OpenAIProvider

def main(args):

    config = Config()

    # create provider and make simple calls
    provider = OpenAIProvider()
    provider.init_provider(args.providerConfig)

    x = provider.embed_query("Hello world")

    agent = Agent("TestAgent", None, provider)
    agent.loop()

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