"""LLM API 调用服务."""

import asyncio
import logging
from typing import Any

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger("travel-helper")


class LLMService:
    """LLM API 调用封装（支持指数退避重试）."""

    def __init__(self):
        self._client = AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_api_base_url,
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
            response_format: 可选的响应格式约束

        Returns:
            LLM 生成的文本内容

        Raises:
            RuntimeError: 重试后仍失败时抛出
        """
        last_error: Exception | None = None

        for attempt in range(settings.llm_max_retries):
            try:
                kwargs: dict[str, Any] = {
                    "model": settings.llm_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                }

                if response_format:
                    kwargs["response_format"] = response_format

                response = await asyncio.wait_for(
                    self._client.chat.completions.create(**kwargs),
                    timeout=settings.llm_timeout,
                )

                content = response.choices[0].message.content
                if not content:
                    raise RuntimeError("LLM 返回空响应")

                logger.info(f"LLM 调用成功 (attempt={attempt + 1})")
                return content

            except asyncio.TimeoutError:
                last_error = TimeoutError(f"LLM 调用超时 ({settings.llm_timeout}s)")
                logger.warning(f"LLM 调用超时, attempt={attempt + 1}")
            except Exception as e:
                last_error = e
                logger.warning(f"LLM 调用失败, attempt={attempt + 1}, error={e}")

            # 指数退避
            if attempt < settings.llm_max_retries - 1:
                delay = 2 ** (attempt + 1)
                logger.info(f"等待 {delay}s 后重试...")
                await asyncio.sleep(delay)

        raise RuntimeError(f"LLM 调用失败，已重试 {settings.llm_max_retries} 次") from last_error
