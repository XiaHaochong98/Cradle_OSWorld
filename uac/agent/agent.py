from typing import List

from uac.provider import LLMProvider
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
        llm_provider : LLMProvider,
    ):
        self.name = name
        self.memory = memory
        self.llm_provider = llm_provider

        self.planner_prompt = "You need to act as ..."

        
    def assemble_prompt(self, user_input: str) -> List[str]:
    
        messages=[
            {
                "role": "system",
                "content": [
                    {
                      "type" : "text",
                      "text" : self.planner_prompt
                    }
                    ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_input
                    },
                    {
                        "type": "image_url",
                        "image_url": 
                        {
                            "url": "https://tellarin.com/images/tellarin.png"
                        }
                    }
                ]
            }
        ]

        return messages

    
    def loop(self):
        
        cfg.continuous_limit = 1

        # Interaction Loop
        loop_count = 0
        command_name = None
        arguments = None
        user_input = ""

        #while True:
        for i in range(1):

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
            msg = "Who are you and what is your version? Are you GPT-4V? Can I send you an image?"
            prompt = self.assemble_prompt(msg)
            response = self.llm_provider.create_completion(prompt)

            print(f'U: {prompt}')
            print(f'A: {response}')
            print()
