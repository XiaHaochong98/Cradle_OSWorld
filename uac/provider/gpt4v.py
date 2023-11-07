from typing import (
    List,
    Dict,
    Tuple,
    Optional,
)

import os
import re
import tiktoken
import backoff
import openai
import base64
from openai.error import (
    APIConnectionError,
    APIError,
    RateLimitError,
    ServiceUnavailableError,
)

from uac.config import Config
from uac.log import Logger
from uac.provider.base_llm import LLMProviderSingleton

cfg = Config()
logger = Logger()

if "OPENAI_API_KEY" not in os.environ:
    raise ValueError(
        "OPENAI_API_KEY environment variable must be set when using OpenAI API."
    )
openai.api_key = os.environ["OPENAI_API_KEY"]
openai.organization = os.environ.get("OPENAI_ORGANIZATION", "")


class GPT4V(LLMProviderSingleton):
    def create_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        stop_tokens: Optional[List[str]] = None,
    ) -> Tuple[str, Dict[str, int]]:
        """The main function to generate a response from the OpenAI API (supports both GPT-4 and GPT-4V).

        Example Usage:
        image_path = "path_to_your_image.jpg"
        base64_image = encode_image(image_path)
        response, info = self.create_completion(
            model="gpt-4-vision-preview",
            messages=[
              {
                "role": "user",
                "content": [
                  {
                    "type": "text",
                    "text": "What’s in this image?"
                  },
                  {
                    "type": "image_url",
                    "image_url": {
                      "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                  }
                ]
              }
            ],
        )
        """

        @backoff.on_exception(
            backoff.constant,
            (APIError, RateLimitError, APIConnectionError, ServiceUnavailableError),
            interval=10,
        )
        def _generate_response_with_retry(
            messages: List[Dict[str, str]],
            model: str,
            temperature: float,
            stop_tokens: Optional[List[str]] = None,
        ) -> Tuple[str, Dict[str, int]]:
            """Send a request to the OpenAI API."""

            if get_mode(model) == "chat":
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    stop=stop_tokens if stop_tokens else None,
                )
                message = response["choices"][0]["message"]["content"]
            else:
                prompt = "\n\n".join(m["content"] for m in messages) + "\n\n"
                response = openai.Completion.create(
                    prompt=prompt,
                    engine=model,
                    temperature=temperature,
                    stop=stop_tokens if stop_tokens else None,
                )
                message = response["choices"][0]["text"]
            info = {
                key: response["usage"][key]
                for key in ["prompt_tokens", "completion_tokens", "total_tokens"]
            }

            return message, info

        return _generate_response_with_retry(
            messages,
            model,
            temperature,
            stop_tokens,
        )


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def num_tokens_from_messages(messages, model):
    """Return the number of tokens used by a list of messages.
    Borrowed from https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-4-1106-vision-preview",
    }:
        raise ValueError("We don't support counting tokens of GPT-4V yet.")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        "gpt-4-1106-preview",
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = (
            4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        )
        tokens_per_name = -1  # if there's a name, the role is omitted
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


MAX_TOKENS = {
    "gpt-3.5-turbo-0301": 4097,
    "gpt-3.5-turbo-0613": 4097,
    "gpt-3.5-turbo-16k-0613": 16385,
}


def get_mode(model: str) -> str:
    """Check if the model is a chat model."""

    if model in [
        "gpt-3.5-turbo-0301",
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        "gpt-4-1106-preview",
        "gpt-4-1106-vision-preview",
    ]:
        return "chat"
    elif model in [
        "davinci-002",
        "gpt-3.5-turbo-instruct-0914",
    ]:
        return "completion"
    else:
        raise ValueError(f"Unknown model: {model}")


def extract_from_response(response: str, backtick="```") -> str:
    """Extract the text between backticks from the response."""
    if backtick == "```":
        # Matches anything between ```<optional label>\n and \n```
        pattern = r"```(?:[a-zA-Z]*)\n?(.*?)\n?```"
    elif backtick == "`":
        pattern = r"`(.*?)`"
    else:
        raise ValueError(f"Unknown backtick: {backtick}")
    match = re.search(
        pattern, response, re.DOTALL
    )  # re.DOTALL makes . match also newlines
    if match:
        extracted_string = match.group(1)
    else:
        extracted_string = ""

    return extracted_string
