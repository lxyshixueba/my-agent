"""城市搜索服务单元测试."""

import pytest
from app.services.city_service import CityService


@pytest.fixture
def city_service():
    return CityService()


class TestCitySearch:
    """城市搜索测试."""

    def test_search_by_chinese_name(self, city_service):
        """通过中文名称搜索."""
        results = city_service.search("北京")
        assert len(results) >= 1
        assert results[0].name == "北京"

    def test_search_by_pinyin(self, city_service):
        """通过拼音搜索."""
        results = city_service.search("beijing")
        assert len(results) >= 1
        assert results[0].name == "北京"

    def test_search_partial_match(self, city_service):
        """部分匹配."""
        results = city_service.search("北")
        assert len(results) >= 1
        names = [r.name for r in results]
        assert "北京" in names

    def test_search_no_result(self, city_service):
        """无匹配结果."""
        results = city_service.search("xyznonexistent")
        assert len(results) == 0

    def test_search_case_insensitive_pinyin(self, city_service):
        """拼音搜索不区分大小写."""
        results_lower = city_service.search("beijing")
        results_upper = city_service.search("BEIJING")
        assert len(results_lower) == len(results_upper)

    def test_search_by_province(self, city_service):
        """通过省份搜索."""
        results = city_service.search("广东省")
        assert len(results) >= 3  # 广州、深圳、珠海等


class TestCityGetByCode:
    """通过城市编码获取城市."""

    def test_get_by_code_exists(self, city_service):
        results = city_service.get_by_code("BJ")
        assert results is not None
        assert results.name == "北京"

    def test_get_by_code_not_found(self, city_service):
        results = city_service.get_by_code("INVALID_CODE")
        assert results is None
