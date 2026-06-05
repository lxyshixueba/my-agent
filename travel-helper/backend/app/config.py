"""环境配置管理."""

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """应用配置."""

    # LLM API 配置
    llm_api_key: str = ""
    llm_api_base_url: str = "https://api.openai.com/v1"

    # 高德地图（可选）
    amap_web_key: str = ""

    # Unsplash（可选）
    unsplash_access_key: str = ""

    # 应用配置
    app_env: str = "development"
    log_level: str = "INFO"

    # LLM 调用配置
    llm_timeout: int = 30
    llm_max_retries: int = 3
    llm_model: str = "gpt-4o"

    # LangSmith 配置
    langsmith_api_key: str = ""
    langsmith_tracing: bool = True  # 默认开启追踪，便于调试
    langsmith_project: str = "travel-helper"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


def apply_langsmith_settings() -> None:
    """应用 LangSmith 环境变量配置.

    在应用启动时调用，确保 LangGraph/LangChain 能够使用 LangSmith 进行追踪。
    """
    if settings.langsmith_tracing and settings.langsmith_api_key:
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
        os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    elif settings.langsmith_tracing:
        # 追踪开启但未配置 API Key，记录警告
        import logging

        logger = logging.getLogger("travel-helper")
        logger.warning("LangSmith 追踪已开启，但 LANGSMITH_API_KEY 未配置，追踪功能将不可用")
