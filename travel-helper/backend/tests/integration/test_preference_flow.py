"""偏好传递集成测试 — 验证偏好参数正确传递到 LLM prompt."""

import pytest
from datetime import date, timedelta

from app.agents.travel_planner_agent import build_prompts
from app.models.travel_plan import (
    TravelPlanCreateRequest,
    CityRef,
    TransportMode,
    Accommodation,
    PreferenceTag,
)


class TestPreferenceFlow:
    """偏好传递流程测试."""

    def test_preferences_included_in_prompt(self):
        """旅行偏好标签被包含在 prompt 中."""
        request = TravelPlanCreateRequest(
            destination=CityRef(name="成都", code="CD"),
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=14),
            transport_mode=TransportMode.high_speed_rail,
            accommodation=Accommodation.premium,
            preferences=[PreferenceTag.food, PreferenceTag.history_culture],
        )

        system_prompt, user_prompt = build_prompts(request)

        assert "美食" in user_prompt
        assert "历史文化" in user_prompt

    def test_accommodation_included_in_prompt(self):
        """住宿偏好被包含在 prompt 中."""
        request = TravelPlanCreateRequest(
            destination=CityRef(name="北京", code="BJ"),
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=9),
            transport_mode=TransportMode.flight,
            accommodation=Accommodation.luxury,
        )

        _, user_prompt = build_prompts(request)

        assert "豪华酒店" in user_prompt

    def test_no_preferences_default_prompt(self):
        """无偏好时使用默认 prompt."""
        request = TravelPlanCreateRequest(
            destination=CityRef(name="上海", code="SH"),
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=3),
            transport_mode=TransportMode.high_speed_rail,
            accommodation=Accommodation.comfort,
        )

        _, user_prompt = build_prompts(request)

        # 无偏好时 prompt 不应包含"旅行偏好"文字
        assert "旅行偏好" not in user_prompt

    def test_special_requirements_included(self):
        """特殊服务要求被包含在 prompt 中."""
        request = TravelPlanCreateRequest(
            destination=CityRef(name="昆明", code="KM"),
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=5),
            transport_mode=TransportMode.flight,
            accommodation=Accommodation.homestay,
            special_requirements="带小孩出行，需要亲子友好景点",
        )

        _, user_prompt = build_prompts(request)

        assert "带小孩出行" in user_prompt
        assert "特殊要求" in user_prompt

    def test_full_prompt_with_all_fields(self):
        """所有字段均被包含在 prompt 中."""
        request = TravelPlanCreateRequest(
            destination=CityRef(name="西安", code="XA"),
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=14),
            transport_mode=TransportMode.high_speed_rail,
            accommodation=Accommodation.premium,
            preferences=[PreferenceTag.food, PreferenceTag.history_culture, PreferenceTag.nature],
            special_requirements="老人出行，行程不要太紧凑",
        )

        _, user_prompt = build_prompts(request)

        assert "西安" in user_prompt
        assert "高铁" in user_prompt
        assert "高档型酒店" in user_prompt
        assert "美食" in user_prompt
        assert "历史文化" in user_prompt
        assert "自然风光" in user_prompt
        assert "老人出行" in user_prompt
