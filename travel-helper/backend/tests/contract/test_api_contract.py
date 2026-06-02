"""API 契约测试 - 验证请求/响应符合 contracts/api-contract.md."""

import pytest
from datetime import date, timedelta
from pydantic import ValidationError

from app.models.travel_plan import (
    TravelPlanCreateRequest,
    CityRef,
    TransportMode,
    Accommodation,
    PreferenceTag,
    TravelPlanResponse,
    DailyItinerary,
    Activity,
)


class TestRequestContract:
    """请求契约测试."""

    def test_minimal_valid_request(self):
        """最小有效请求（必填字段）."""
        req = TravelPlanCreateRequest(
            destination=CityRef(name="北京", code="BJ"),
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=14),
            transport_mode=TransportMode.high_speed_rail,
            accommodation=Accommodation.premium,
        )
        assert req.destination.name == "北京"
        assert req.preferences is None
        assert req.special_requirements is None

    def test_full_request(self):
        """完整请求（含可选字段）."""
        req = TravelPlanCreateRequest(
            destination=CityRef(name="北京", code="BJ"),
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=14),
            transport_mode=TransportMode.high_speed_rail,
            accommodation=Accommodation.premium,
            preferences=["food", "history_culture"],
            special_requirements="带老人出行",
        )
        assert len(req.preferences) == 2
        assert req.special_requirements == "带老人出行"

    def test_response_contract(self):
        """响应格式符合契约."""
        response = TravelPlanResponse(
            request_id="req-test-001",
            destination="北京",
            days=5,
            daily_itineraries=[
                DailyItinerary(
                    day=1,
                    date="2026-07-01",
                    theme="历史文化之旅",
                    activities=[
                        Activity(
                            type="attraction",
                            name="故宫博物院",
                            description="中国明清两代的皇家宫殿",
                            time_slot="morning",
                            duration_minutes=180,
                        )
                    ],
                )
            ],
            generated_at="2026-06-02T10:00:00+08:00",
        )
        assert response.request_id is not None
        assert len(response.daily_itineraries) == 1
        assert response.daily_itineraries[0].activities[0].type == "attraction"
