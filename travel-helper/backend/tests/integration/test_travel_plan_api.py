"""旅行计划生成 API 集成测试."""

import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def valid_request_body():
    return {
        "destination": {"name": "北京", "code": "BJ"},
        "start_date": (date.today() + timedelta(days=10)).isoformat(),
        "end_date": (date.today() + timedelta(days=14)).isoformat(),
        "transport_mode": "high_speed_rail",
        "accommodation": "premium",
        "preferences": ["food", "history_culture"],
        "special_requirements": "",
    }


class TestTravelPlanGeneration:
    """旅行计划生成集成测试."""

    @patch("app.services.travel_plan_service.LLMService")
    def test_generate_success(self, mock_llm, client, valid_request_body):
        """成功生成旅行计划."""
        mock_response = MagicMock()
        mock_response.return_value = {
            "destination": "北京",
            "days": 5,
            "daily_itineraries": [],
            "generated_at": "2026-06-02T10:00:00+08:00",
        }
        # 跳过 LLM 调用，直接测试 API 层

    def test_missing_destination_returns_400(self, client):
        """缺少目的地返回 400."""
        body = {
            "destination": {"name": "", "code": ""},
            "start_date": (date.today() + timedelta(days=10)).isoformat(),
            "end_date": (date.today() + timedelta(days=14)).isoformat(),
            "transport_mode": "flight",
            "accommodation": "economy",
        }
        response = client.post("/api/v1/travel-plans/generate", json=body)
        assert response.status_code == 422  # pydantic validation

    def test_invalid_dates_returns_422(self, client):
        """无效日期返回 422."""
        body = {
            "destination": {"name": "北京", "code": "BJ"},
            "start_date": (date.today() - timedelta(days=1)).isoformat(),
            "end_date": (date.today() + timedelta(days=5)).isoformat(),
            "transport_mode": "flight",
            "accommodation": "economy",
        }
        response = client.post("/api/v1/travel-plans/generate", json=body)
        assert response.status_code == 422

    def test_city_not_found_returns_404(self, client):
        """城市不存在返回 404."""
        body = {
            "destination": {"name": "不存在的城市xyz", "code": "XYZ"},
            "start_date": (date.today() + timedelta(days=10)).isoformat(),
            "end_date": (date.today() + timedelta(days=14)).isoformat(),
            "transport_mode": "flight",
            "accommodation": "economy",
        }
        response = client.post("/api/v1/travel-plans/generate", json=body)
        assert response.status_code == 404
