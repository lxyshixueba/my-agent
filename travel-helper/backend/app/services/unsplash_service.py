"""Unsplash 景点图片获取服务.

基于景点名称搜索并返回图片 URL。
"""

import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger("travel-helper")


class UnsplashService:
    """Unsplash 图片搜索服务.

    基于景点名称搜索 Unsplash 图片，返回合适的图片 URL。
    """

    # Unsplash 搜索 API 端点
    BASE_URL = "https://api.unsplash.com/search/photos"

    def __init__(self) -> None:
        self._access_key = settings.unsplash_access_key
        # 简单缓存：{search_query: image_url}
        self._cache: dict[str, str] = {}

    async def search_image(self, query: str) -> Optional[str]:
        """根据搜索词获取一张合适的图片 URL.

        Args:
            query: 搜索关键词（景点名称）

        Returns:
            图片 URL（small 尺寸），如果没有可用图片则返回 None
        """
        if not query or not query.strip():
            return None

        query = query.strip()
        if query in self._cache:
            logger.debug(f"Unsplash 缓存命中: {query}")
            return self._cache[query]

        # 如果未配置 Unsplash Key，返回 None
        if not self._access_key:
            logger.debug("Unsplash API Key 未配置，跳过图片搜索")
            return None

        try:
            import httpx

            async with httpx.AsyncClient(timeout=10.0) as http_client:
                response = await http_client.get(
                    self.BASE_URL,
                    params={
                        "query": query,
                        "per_page": 1,
                        "orientation": "landscape",
                    },
                    headers={
                        "Authorization": f"Client-ID {self._access_key}",
                    },
                )

                if response.status_code != 200:
                    logger.warning(
                        f"Unsplash API 请求失败: status={response.status_code}, query={query}"
                    )
                    return None

                data = response.json()
                results = data.get("results", [])
                if not results:
                    logger.debug(f"Unsplash 未找到图片: {query}")
                    return None

                # 使用 small 尺寸的图片 URL
                image_url = results[0].get("urls", {}).get("small")
                if image_url:
                    self._cache[query] = image_url
                    logger.info(f"Unsplash 图片已获取: {query}")
                    return image_url

                return None

        except Exception as e:
            logger.warning(f"Unsplash 图片搜索异常: {query}, error={e}")
            return None


# 全局单例
unsplash_service = UnsplashService()
