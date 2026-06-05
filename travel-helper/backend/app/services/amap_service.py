"""高德地图 MCP 服务封装.

封装高德地图 Web 服务 API（POI 搜索、天气查询、路线规划、地理编码/逆地理编码），
通过 httpx 调用，JSON 返回。API Key 通过 .env 配置管理，不硬编码。
"""

import logging
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger("travel-helper")


class AMapService:
    """高德地图 Web 服务 API 代理.

    封装以下 API：
    - POI 搜索: /v3/place/text
    - 天气查询: /v3/weather/weatherInfo
    - 路线规划: /v3/direction/driving
    - 地理编码: /v3/geocode/geo
    - 逆地理编码: /v3/geocode/regeo
    """

    # 高德 Web 服务 API 基础 URL
    BASE_URL = "https://restapi.amap.com/v3"

    def __init__(self) -> None:
        self._api_key = settings.amap_web_key
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=15.0,
        )

    async def close(self) -> None:
        """关闭 HTTP 客户端."""
        await self._client.aclose()

    # =========================================================================
    # POI 搜索
    # =========================================================================

    async def search_poi(
        self,
        keyword: str,
        city: str = "",
        types: str = "",
        page: int = 1,
        offset: int = 20,
    ) -> list[dict]:
        """搜索 POI（兴趣点）.

        Args:
            keyword: 搜索关键词（景点名、酒店名等）
            city: 城市名称或编码（可选，限定搜索范围）
            types: POI 类型编码（可选，如 "150100" 表示风景名胜）
            page: 页码（从 1 开始）
            offset: 每页返回数量

        Returns:
            POI 列表，每个包含 name, location(lng,lat), address, typecode 等字段
        """
        if not self._api_key:
            logger.warning("高德 API Key 未配置，返回空结果")
            return []

        try:
            response = await self._client.get(
                "/place/text",
                params={
                    "key": self._api_key,
                    "keywords": keyword,
                    "city": city,
                    "types": types,
                    "page": page,
                    "offset": offset,
                    "extensions": "all",
                    "output": "JSON",
                },
            )
            data = response.json()
            if data.get("status") != "1":
                logger.warning(f"高德 POI 搜索失败: info={data.get('info', '')}, keyword={keyword}")
                return []
            return data.get("pois", [])
        except Exception as e:
            logger.error(f"高德 POI 搜索异常: {e}, keyword={keyword}")
            return []

    # =========================================================================
    # 天气查询
    # =========================================================================

    async def get_weather(
        self,
        city_code: str,
        extensions: str = "base",
    ) -> Optional[dict]:
        """查询指定城市的天气.

        Args:
            city_code: 城市 adcode（如北京为 "110000"）
            extensions: "base" 返回实况天气，"all" 返回预报天气

        Returns:
            天气数据字典
        """
        if not self._api_key:
            logger.warning("高德 API Key 未配置，返回 None")
            return None

        try:
            response = await self._client.get(
                "/weather/weatherInfo",
                params={
                    "key": self._api_key,
                    "city": city_code,
                    "extensions": extensions,
                    "output": "JSON",
                },
            )
            data = response.json()
            if data.get("status") != "1":
                logger.warning(f"高德天气查询失败: info={data.get('info', '')}, city={city_code}")
                return None
            lives = data.get("lives", [])
            return lives[0] if lives else None
        except Exception as e:
            logger.error(f"高德天气查询异常: {e}, city={city_code}")
            return None

    # =========================================================================
    # 路线规划（驾车）
    # =========================================================================

    async def get_driving_route(
        self,
        origin: str,
        destination: str,
        strategy: str = "0",
    ) -> Optional[dict]:
        """获取驾车路线规划.

        Args:
            origin: 起点经纬度（格式: "经度,纬度"）
            destination: 终点经纬度（格式: "经度,纬度"）
            strategy: 路线策略，0=速度优先，1=费用优先，2=距离最短

        Returns:
            路线数据字典（包含 distance, duration, steps 等）
        """
        if not self._api_key:
            logger.warning("高德 API Key 未配置，返回 None")
            return None

        try:
            response = await self._client.get(
                "/direction/driving",
                params={
                    "key": self._api_key,
                    "origin": origin,
                    "destination": destination,
                    "strategy": strategy,
                    "output": "JSON",
                },
            )
            data = response.json()
            if data.get("status") != "1":
                logger.warning(f"高德路线规划失败: info={data.get('info', '')}")
                return None
            route = data.get("route", {})
            paths = route.get("paths", [])
            return paths[0] if paths else None
        except Exception as e:
            logger.error(f"高德路线规划异常: {e}, origin={origin}, dest={destination}")
            return None

    # =========================================================================
    # 地理编码（地址/城市名 → 经纬度）
    # =========================================================================

    async def geocode(
        self,
        address: str,
        city: str = "",
    ) -> Optional[tuple[float, float]]:
        """将地址/城市名转换为经纬度坐标.

        Args:
            address: 地址或城市名称
            city: 限定城市（可选）

        Returns:
            (lng, lat) 经纬度元组，失败返回 None
        """
        if not self._api_key:
            logger.warning("高德 API Key 未配置，返回 None")
            return None

        try:
            response = await self._client.get(
                "/geocode/geo",
                params={
                    "key": self._api_key,
                    "address": address,
                    "city": city,
                    "output": "JSON",
                },
            )
            data = response.json()
            if data.get("status") != "1":
                logger.warning(f"高德地理编码失败: info={data.get('info', '')}, address={address}")
                return None
            geocodes = data.get("geocodes", [])
            if geocodes:
                location = geocodes[0].get("location", "")  # 格式: "lng,lat"
                if location:
                    lng, lat = location.split(",")
                    return (float(lng), float(lat))
            return None
        except Exception as e:
            logger.error(f"高德地理编码异常: {e}, address={address}")
            return None

    # =========================================================================
    # 逆地理编码（经纬度 → 地址）
    # =========================================================================

    async def regeo(
        self,
        lng: float,
        lat: float,
    ) -> Optional[str]:
        """将经纬度坐标转换为地址描述.

        Args:
            lng: 经度
            lat: 纬度

        Returns:
            地址描述字符串，失败返回 None
        """
        if not self._api_key:
            logger.warning("高德 API Key 未配置，返回 None")
            return None

        try:
            response = await self._client.get(
                "/geocode/regeo",
                params={
                    "key": self._api_key,
                    "location": f"{lng},{lat}",
                    "output": "JSON",
                },
            )
            data = response.json()
            if data.get("status") != "1":
                logger.warning(f"高德逆地理编码失败: info={data.get('info', '')}")
                return None
            regeocode = data.get("regeocode", {})
            return regeocode.get("formatted_address", "")
        except Exception as e:
            logger.error(f"高德逆地理编码异常: {e}, lng={lng}, lat={lat}")
            return None


# 全局单例
amap_service = AMapService()
