"""环境配置管理."""

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

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
