"""城市搜索服务."""

from app.models.city import City, load_cities


class CityService:
    """城市搜索与管理服务."""

    def __init__(self):
        self._cities: list[City] = load_cities()

    def search(self, query: str) -> list[City]:
        """搜索城市（支持名称和拼音匹配）.

        Args:
            query: 搜索关键字（城市名称或拼音前缀）

        Returns:
            匹配的城市列表
        """
        if not query or not query.strip():
            return []

        q = query.strip().lower()
        results = []

        # 按优先级匹配：名称 > 拼音 > 省份
        for city in self._cities:
            if q in city.name.lower() or city.pinyin.lower().startswith(q) or q in city.province.lower():
                results.append(city)

        # 按名称长度排序（短名称优先，通常更精确）
        results.sort(key=lambda c: (len(c.name), c.name))
        return results

    def get_by_code(self, code: str) -> City | None:
        """通过城市编码获取城市.

        Args:
            code: 城市编码

        Returns:
            城市对象，未找到返回 None
        """
        for city in self._cities:
            if city.code == code:
                return city
        return None

    def exists(self, name: str, code: str) -> bool:
        """验证城市是否存在于数据集中.

        Args:
            name: 城市名称
            code: 城市编码

        Returns:
            城市是否存在
        """
        return any(c.name == name and c.code == code for c in self._cities)


# 模块级单例，供路由直接导入
city_service = CityService()
