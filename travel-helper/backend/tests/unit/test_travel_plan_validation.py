"""旅行计划请求模型日期校验单元测试."""

import pytest
from datetime import date, timedelta
from app.models.travel_plan import TravelPlanCreateRequest, CityRef
from app.models.travel_plan import TransportMode, Accommodation


class TestDateValidation:
    """日期校验测试."""

    def test_valid_dates(self):
        """有效日期范围."""
        future = date.today() + timedelta(days=30)
        req = TravelPlanCreateRequest(
            destination=CityRef(name="北京", code="BJ"),
            start_date=date.today() + timedelta(days=10),
            end_date=future,
            transport_mode=TransportMode.high_speed_rail,
            accommodation=Accommodation.premium,
        )
        assert req.start_date < req.end_date

    def test_start_date_in_past_raises_error(self):
        """出发日期为过去日期."""
        with pytest.raises(Exception):
            TravelPlanCreateRequest(
                destination=CityRef(name="北京", code="BJ"),
                start_date=date.today() - timedelta(days=1),
                end_date=date.today() + timedelta(days=5),
                transport_mode=TransportMode.flight,
                accommodation=Accommodation.economy,
            )

    def test_end_date_before_start_date_raises_error(self):
        """返回日期早于出发日期."""
        with pytest.raises(Exception):
            TravelPlanCreateRequest(
                destination=CityRef(name="北京", code="BJ"),
                start_date=date.today() + timedelta(days=10),
                end_date=date.today() + timedelta(days=5),
                transport_mode=TransportMode.flight,
                accommodation=Accommodation.economy,
            )

    def test_days_over_30_raises_error(self):
        """出行天数超过30天."""
        with pytest.raises(Exception):
            TravelPlanCreateRequest(
                destination=CityRef(name="北京", code="BJ"),
                start_date=date.today() + timedelta(days=1),
                end_date=date.today() + timedelta(days=32),
                transport_mode=TransportMode.flight,
                accommodation=Accommodation.economy,
            )


class TestEnumValidation:
    """枚举值校验测试."""

    def test_valid_transport_modes(self):
        """所有交通方式均有效."""
        for mode in TransportMode:
            req = TravelPlanCreateRequest(
                destination=CityRef(name="北京", code="BJ"),
                start_date=date.today() + timedelta(days=1),
                end_date=date.today() + timedelta(days=3),
                transport_mode=mode,
                accommodation=Accommodation.economy,
            )
            assert req.transport_mode == mode

    def test_valid_accommodations(self):
        """所有住宿偏好均有效."""
        for acc in Accommodation:
            req = TravelPlanCreateRequest(
                destination=CityRef(name="北京", code="BJ"),
                start_date=date.today() + timedelta(days=1),
                end_date=date.today() + timedelta(days=3),
                transport_mode=TransportMode.flight,
                accommodation=acc,
            )
            assert req.accommodation == acc

    def test_special_requirements_max_length(self):
        """特殊服务要求长度校验."""
        long_text = "a" * 501
        with pytest.raises(Exception):
            TravelPlanCreateRequest(
                destination=CityRef(name="北京", code="BJ"),
                start_date=date.today() + timedelta(days=1),
                end_date=date.today() + timedelta(days=3),
                transport_mode=TransportMode.flight,
                accommodation=Accommodation.economy,
                special_requirements=long_text,
            )
