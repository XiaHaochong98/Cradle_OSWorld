from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)
import os
import numpy as np
import backoff
import openai

from uac.config import Config
from uac.log import Logger
from uac.provider.base_embedding import EmbeddingProvider

cfg = Config()
logger = Logger()

if "OPENAI_API_KEY" not in os.environ:
    raise ValueError(
        "OPENAI_API_KEY environment variable must be set when using OpenAI API."
    )
openai.api_key = os.environ["OPENAI_API_KEY"]
openai.organization = os.environ.get("OPENAI_ORGANIZATION", "")


class OpenAIEmbeddings(EmbeddingProvider):
    """OpenAI embedding models.
    Code modified based on langchain.

    To use, you should have the ``openai`` python package installed, and the
    environment variable ``OPENAI_API_KEY`` set with your API key.
    """

    client: Any = openai.Embedding
    model: str = "text-embedding-ada-002"
    deployment: str = model  # to support Azure OpenAI Service custom deployment names
    openai_api_version: Optional[str] = None
    # to support Azure OpenAI Service custom endpoints
    openai_api_base: Optional[str] = None
    # to support Azure OpenAI Service custom endpoints
    openai_api_type: Optional[str] = None
    # to support explicit proxy for OpenAI
    openai_proxy: Optional[str] = None
    embedding_ctx_length: int = 8191
    """The maximum number of tokens to embed at once."""
    openai_api_key: Optional[str] = None
    openai_organization: Optional[str] = None
    allowed_special: Union[Literal["all"], Set[str]] = set()
    disallowed_special: Union[Literal["all"], Set[str], Sequence[str]] = "all"
    chunk_size: int = 1000
    """Maximum number of texts to embed in each batch"""
    max_retries: int = 6
    """Maximum number of retries to make when generating."""
    request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    """Timeout in seconds for the OpenAPI request."""
    headers: Any = None
    tiktoken_model_name: Optional[str] = None
    """The model name to pass to tiktoken when using this class. 
    Tiktoken is used to count the number of tokens in documents to constrain 
    them to be under a certain limit. By default, when set to None, this will 
    be the same as the embedding model name. However, there are some cases 
    where you may want to use this Embedding class with a model name not 
    supported by tiktoken. This can include when using Azure embeddings or 
    when using one of the many model providers that expose an OpenAI-like 
    API but with different models. In those cases, in order to avoid erroring 
    when tiktoken is called, you can specify a model name to use here."""
    show_progress_bar: bool = False
    """Whether to show a progress bar when embedding."""
    skip_empty: bool = False
    """Whether to skip empty strings when embedding or raise an error.
    Defaults to not skipping."""

    @property
    def _invocation_params(self) -> Dict:
        openai_args = {
            "model": self.model,
            "request_timeout": self.request_timeout,
            "headers": self.headers,
            "api_key": self.openai_api_key,
            "organization": self.openai_organization,
            "api_base": self.openai_api_base,
            "api_type": self.openai_api_type,
            "api_version": self.openai_api_version,
        }
        if self.openai_api_type in ("azure", "azure_ad", "azuread"):
            openai_args["engine"] = self.deployment
        if self.openai_proxy:
            try:
                import openai
            except ImportError:
                raise ImportError(
                    "Could not import openai python package. "
                    "Please install it with `pip install openai`."
                )

            openai.proxy = {
                "http": self.openai_proxy,
                "https": self.openai_proxy,
            }  # type: ignore[assignment]  # noqa: E501
        return openai_args

    def embed_with_retry(self, **kwargs: Any) -> Any:
        """Use backoff to retry the embedding call."""

        @backoff.on_exception(
            backoff.expo,
            (
                openai.error.APIError,
                openai.error.RateLimitError,
                openai.error.APIConnectionError,
                openai.error.ServiceUnavailableError,
            ),
            max_tries=self.max_retries,
            max_value=10,
            min_value=4,
            jitter=None,
        )
        def _embed_with_retry(**kwargs: Any) -> Any:
            response = self.client.create(**kwargs)
            if any(len(d["embedding"]) == 1 for d in response["data"]):
                raise openai.error.APIError("OpenAI API returned an empty embedding")
            return response

        return _embed_with_retry(**kwargs)

    def _get_len_safe_embeddings(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        embeddings: List[List[float]] = [[] for _ in range(len(texts))]
        try:
            import tiktoken
        except ImportError:
            raise ImportError(
                "Could not import tiktoken python package. "
                "This is needed in order to for OpenAIEmbeddings. "
                "Please install it with `pip install tiktoken`."
            )

        tokens = []
        indices = []
        model_name = self.tiktoken_model_name or self.model
        try:
            encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            logger.warning("Warning: model not found. Using cl100k_base encoding.")
            model = "cl100k_base"
            encoding = tiktoken.get_encoding(model)
        for i, text in enumerate(texts):
            if self.model.endswith("001"):
                # See: https://github.com/openai/openai-python/issues/418#issuecomment-1525939500
                # replace newlines, which can negatively affect performance.
                text = text.replace("\n", " ")
            token = encoding.encode(
                text,
                allowed_special=self.allowed_special,
                disallowed_special=self.disallowed_special,
            )
            for j in range(0, len(token), self.embedding_ctx_length):
                tokens.append(token[j : j + self.embedding_ctx_length])
                indices.append(i)

        batched_embeddings: List[List[float]] = []
        _chunk_size = self.chunk_size

        if self.show_progress_bar:
            try:
                from tqdm.auto import tqdm

                _iter = tqdm(range(0, len(tokens), _chunk_size))
            except ImportError:
                _iter = range(0, len(tokens), _chunk_size)
        else:
            _iter = range(0, len(tokens), _chunk_size)

        for i in _iter:
            response = self.embed_with_retry(
                input=tokens[i : i + self.chunk_size],
                **self._invocation_params,
            )
            batched_embeddings.extend(r["embedding"] for r in response["data"])

        results: List[List[List[float]]] = [[] for _ in range(len(texts))]
        num_tokens_in_batch: List[List[int]] = [[] for _ in range(len(texts))]
        for i in range(len(indices)):
            if self.skip_empty and len(batched_embeddings[i]) == 1:
                continue
            results[indices[i]].append(batched_embeddings[i])
            num_tokens_in_batch[indices[i]].append(len(tokens[i]))

        for i in range(len(texts)):
            _result = results[i]
            if len(_result) == 0:
                average = self.embed_with_retry(
                    input="",
                    **self._invocation_params,
                )[
                    "data"
                ][0]["embedding"]
            else:
                average = np.average(_result, axis=0, weights=num_tokens_in_batch[i])
            embeddings[i] = (average / np.linalg.norm(average)).tolist()

        return embeddings

    def embed_documents(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        """Call out to OpenAI's embedding endpoint for embedding search docs.

        Args:
            texts: The list of texts to embed.

        Returns:
            List of embeddings, one for each text.
        """
        # NOTE: to keep things simple, we assume the list may contain texts longer
        #       than the maximum context and use length-safe embedding function.
        return self._get_len_safe_embeddings(texts)

    def embed_query(self, text: str) -> List[float]:
        """Call out to OpenAI's embedding endpoint for embedding query text.

        Args:
            text: The text to embed.

        Returns:
            Embedding for the text.
        """
        return self.embed_documents([text])[0]

    def get_embedding_dim(self) -> int:
        """Get the embedding dimension."""
        if self.model == "text-embedding-ada-002":
            embedding_dim = 1536
        else:
            raise ValueError(f"Unknown embedding model: {self.model}")
        return embedding_dim
