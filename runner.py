import os
import sys
import argparse
import time

from uac.agent import Agent
from uac.config import Config
from uac.provider.openai import OpenAiProvider

def main(args):

    config = Config()

    # create provider and make simple calls
    provider = OpenAiProvider()
    provider.init_provider(args.providerConfig)

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