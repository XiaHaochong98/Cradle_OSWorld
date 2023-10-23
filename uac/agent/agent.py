from typing import List

from uac.provider import LLMProviderSingleton
from uac.config import Config
from uac.log import Logger

cfg = Config()
logger = Logger()


# Here the Agent using the LLM provider direcly, but we could have a Planner class to wrap the planning prompts.
# This is an incomplete example with not complete quality code, just to bootstrap the repo.

class Agent:

    def __init__(
        self,
        name,
        memory,
        llm : LLMProviderSingleton,
    ):
        self.name = name
        self.memory = memory
        self.llm = llm

        self.planner_prompt = "You need to act as ..."

        
    def assemble_prompt(self, external_input: str) -> List[str]:
    
        messages = [
            {"role": "system", "content": self.planner_prompt},
            {"role": "user", "content": external_input},
        ]

        return messages

    
    def loop(self):
        
        cfg.continuous_limit = 1

        # Interaction Loop
        loop_count = 0
        command_name = None
        arguments = None
        user_input = ""

        while True:

            # Stop if limit is reached
            loop_count += 1
            if (
                cfg.continuous_mode and 
                cfg.continuous_limit > 0 and
                loop_count > cfg.continuous_limit
            ):
                logger.write(f"Continuous Limit Reached: {cfg.continuous_limit} iteractions")
                break

            # Call provider
            msg = "Hello world"
            prompt = self.assemble_prompt(msg)
            response = self.provider.create_completion(prompt)

            print(f'U: {prompt}')
            print(f'A: {response}')
            print()
