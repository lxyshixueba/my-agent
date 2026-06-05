"""天气数据查询服务.

基于目的地城市和日期查询天气数据，提供简单的缓存层。
"""

import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger("travel-helper")


class WeatherService:
    """天气数据查询与缓存服务.

    在实际生产环境中，这里会调用高德天气 API 或第三方天气服务。
    当前阶段使用模拟数据，确保功能链路畅通。
    """

    def __init__(self) -> None:
        # 简单内存缓存：{(city_name, date_str): weather_data}
        self._cache: dict[tuple[str, str], dict] = {}

    async def get_weather(
        self,
        city_name: str,
        date_str: str,
    ) -> Optional[dict]:
        """获取指定城市和日期的天气数据.

        Args:
            city_name: 城市名称（如"北京"）
            date_str: 日期字符串（如"2026-07-01"）

        Returns:
            天气数据字典，格式：
            {
                "date": "2026-07-01",
                "condition": "晴",
                "temperature": {"low": 22, "high": 32},
                "wind_speed": "微风",
            }
            如果无法获取则返回 None
        """
        cache_key = (city_name, date_str)
        if cache_key in self._cache:
            logger.debug(f"天气缓存命中: {city_name} {date_str}")
            return self._cache[cache_key]

        # TODO: 实际调用高德天气 API（需要高德 AMAP_WEB_KEY 支持）
        # 目前返回模拟数据
        weather_data = self._generate_mock_weather(city_name, date_str)

        if weather_data:
            self._cache[cache_key] = weather_data
            logger.info(f"天气数据已获取并缓存: {city_name} {date_str}")

        return weather_data

    def _generate_mock_weather(self, city_name: str, date_str: str) -> dict:
        """生成模拟天气数据.

        Args:
            city_name: 城市名称
            date_str: 日期字符串

        Returns:
            模拟天气数据字典
        """
        import hashlib

        # 使用城市和日期的哈希值生成"随机"但可复现的天气
        hash_val = int(
            hashlib.md5(f"{city_name}{date_str}".encode()).hexdigest(),
            16,
        )

        conditions = ["晴", "多云", "阴", "小雨", "阵雨"]
        condition = conditions[hash_val % len(conditions)]

        # 根据哈希值生成合理的温度范围
        base_temp = 15 + (hash_val % 20)  # 15-34
        low = base_temp - 5
        high = base_temp + 5

        wind_speeds = ["微风", "1-2级", "3-4级", "4-5级"]
        wind_speed = wind_speeds[hash_val % len(wind_speeds)]

        return {
            "date": date_str,
            "condition": condition,
            "temperature": {"low": low, "high": high},
            "wind_speed": wind_speed,
        }


# 全局单例
weather_service = WeatherService()
