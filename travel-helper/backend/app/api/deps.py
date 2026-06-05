"""依赖注入模块.

提供 FastAPI 依赖注入函数，用于获取高德 MCP 客户端、
LLM 客户端、LangGraph 状态图实例等共享资源。
"""

from typing import Generator

from app.services.amap_service import AMapService, amap_service
from app.services.llm_service import LLMService, llm_service
from app.services.weather_service import WeatherService, weather_service
from app.services.unsplash_service import UnsplashService, unsplash_service


def get_amap_service() -> AMapService:
    """获取高德地图服务实例."""
    return amap_service


def get_llm_service() -> LLMService:
    """获取 LLM 服务实例."""
    return llm_service


def get_weather_service() -> WeatherService:
    """获取天气服务实例."""
    return weather_service


def get_unsplash_service() -> UnsplashService:
    """获取 Unsplash 图片服务实例."""
    return unsplash_service


def get_replan_graph() -> Generator:
    """获取 LangGraph 重新规划 StateGraph 实例.

    Yields:
        编译好的 StateGraph 实例
    """
    from app.agents.itinerary_agent import get_replan_graph as _get_graph

    graph = _get_graph()
    yield graph
