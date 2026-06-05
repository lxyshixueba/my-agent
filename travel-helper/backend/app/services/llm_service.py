"""LLM API 调用服务（LangChain 版本）.

使用 LangChain ChatOpenAI 替代原始 OpenAI SDK，
内置重试、超时、结构化输出能力。
"""

import logging
from typing import Any, Type

from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger("travel-helper")


class LLMService:
    """LLM API 调用封装（LangChain ChatOpenAI + 内置重试/超时）."""

    def __init__(self) -> None:
        self._model_name = settings.llm_model
        self._api_key = settings.llm_api_key
        self._base_url = settings.llm_api_base_url
        self._timeout = settings.llm_timeout
        self._max_retries = settings.llm_max_retries

    def _get_llm(self) -> "ChatOpenAI":
        """获取 LangChain ChatOpenAI 实例."""
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=self._model_name,
            api_key=self._api_key,
            base_url=self._base_url,
            temperature=0.7,
            timeout=self._timeout,
            max_retries=self._max_retries,
        )

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: dict[str, Any] | None = None,
    ) -> str:
        """调用 LLM 生成内容.

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            response_format: 可选的响应格式约束（LangChain 中不使用，请用 with_structured_output）

        Returns:
            LLM 生成的文本内容

        Raises:
            RuntimeError: 重试后仍失败时抛出
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = self._get_llm()
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        last_error: Exception | None = None
        for attempt in range(self._max_retries):
            try:
                response = await llm.ainvoke(messages)
                content = response.content
                if not content:
                    raise RuntimeError("LLM 返回空响应")

                logger.info(f"LLM 调用成功 (attempt={attempt + 1})")
                return content

            except Exception as e:
                last_error = e
                logger.warning(f"LLM 调用失败, attempt={attempt + 1}, error={e}")

        raise RuntimeError(f"LLM 调用失败，已重试 {self._max_retries} 次") from last_error

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        output_model: Type[BaseModel],
    ) -> BaseModel:
        """使用结构化输出调用 LLM.

        使用 LangChain 的 with_structured_output 方法，
        LLM 返回结果自动按 Pydantic 模型解析和校验。

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            output_model: Pydantic 输出模型类

        Returns:
            解析后的 Pydantic 模型实例
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = self._get_llm().with_structured_output(output_model)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        result = await llm.ainvoke(messages)
        return result


# 全局单例
llm_service = LLMService()
