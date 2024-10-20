from typing import (
    Any,
    Optional,
    Sequence,
)
from loguru import logger

from llama_index.legacy.bridge.pydantic import Field
from llama_index.core.llms.custom import (
    llm_chat_callback,
    llm_completion_callback,
)
from llama_index.core.llms import LLM
from llama_index.core.base.llms.types import (
    ChatMessage,
    ChatResponse,
    ChatResponseAsyncGen,
    ChatResponseGen,
    CompletionResponse,
    CompletionResponseAsyncGen,
    CompletionResponseGen,
    LLMMetadata,
    TextBlock,
)

DEFAULT_MODEL = "qwen-max"
#export DASHSCOPE_API_KEY="YOUR_KEY"

import random
from http import HTTPStatus
import dashscope

class QwenUnofficial(LLM) :
    model: str = Field(
        default=DEFAULT_MODEL, description="The QWen model to use."
    )

    max_tokens: Optional[int] = Field(
        description="The maximum number of tokens to generate.",
        gt=0,
    )

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> None :

        super().__init__(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

    @llm_chat_callback()
    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        logger.info("Sending prompt to Qwen...")
        for m in messages:
            logger.debug(f"{m.role}:")
            logger.debug(f"{m.content}")

        response = dashscope.Generation.call(
            model=dashscope.Generation.Models.qwen_max,
            messages=[
                { "role": m.role, "content": m.content }
                for m in messages
            ],
            result_format='message',
        )
        message = response.output.choices[0].message
        logger.debug(f"{message.role}:")
        logger.debug(f"{message.content}")
        return ChatResponse(message=ChatMessage(role=message.role, content=message.content))

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=6000,
            num_output=self.max_tokens or -1,
            # is_chat_model=is_chat_model(model=self._get_model_name()),
            is_chat_model=True,
            is_function_calling_model=False,
            # is_function_calling_model=is_function_calling_model(
            #     model=self._get_model_name()
            # ),
            model_name=self.model,
        )

    # 下面是实现Interface必要的方法
    # 但这里用不到，所以都是pass
    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        pass

    @llm_completion_callback()
    async def astream_complete() -> CompletionResponseAsyncGen:
        pass

    async def _astream_chat() -> ChatResponseAsyncGen:
        pass

    @llm_chat_callback()
    async def astream_chat() -> ChatResponseAsyncGen:
        pass

    @llm_chat_callback()
    def stream_chat() -> ChatResponseGen:
        pass
    
    @llm_completion_callback()
    def stream_complete() -> CompletionResponseGen:
        pass

    @llm_chat_callback()
    async def achat() -> ChatResponse:
        pass
    
    @llm_completion_callback()
    async def acomplete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        pass
