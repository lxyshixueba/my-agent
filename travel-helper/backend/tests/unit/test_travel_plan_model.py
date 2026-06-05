"""旅行计划完整数据模型 Pydantic 字段校验与预算计算单元测试."""

import pytest
from datetime import date
from pydantic import ValidationError

from app.models.travel_plan import (
    DestinationCity,
    DateRange,
    TravelPreferences,
    BudgetBreakdown,
    TimeSlot,
    AttractionDetail,
    AccommodationPlan,
    DiningPlan,
    TransportationPlan,
    TemperatureRange,
    WeatherInfo,
    DailyItineraryDetail,
    TravelPlanFull,
)


class TestDestinationCity:
    """DestinationCity 模型校验测试."""

    def test_minimal_valid(self):
        """最小有效创建."""
        city = DestinationCity(name="北京")
        assert city.name == "北京"
        assert city.latitude == 0.0
        assert city.longitude == 0.0

    def test_full_valid(self):
        """完整有效创建."""
        city = DestinationCity(name="上海", latitude=31.2304, longitude=121.4737)
        assert city.name == "上海"
        assert city.latitude == 31.2304
        assert city.longitude == 121.4737

    def test_empty_name_raises_error(self):
        """空名称应校验失败."""
        with pytest.raises(ValidationError):
            DestinationCity(name="")


class TestDateRange:
    """DateRange 模型校验测试."""

    def test_valid_range(self):
        """有效日期范围."""
        dr = DateRange(start_date=date(2026, 7, 1), end_date=date(2026, 7, 15))
        assert dr.start_date == date(2026, 7, 1)
        assert dr.end_date == date(2026, 7, 15)


class TestTravelPreferences:
    """TravelPreferences 模型校验测试."""

    def test_default_values(self):
        """默认值创建."""
        prefs = TravelPreferences()
        assert prefs.accommodation_type == ""
        assert prefs.transportation == ""
        assert prefs.tags == []
        assert prefs.special_requests == ""

    def test_full_values(self):
        """完整值创建."""
        prefs = TravelPreferences(
            accommodation_type="高档型酒店",
            transportation="高铁",
            tags=["景点观光", "美食"],
            special_requests="带老人出行",
        )
        assert len(prefs.tags) == 2


class TestBudgetBreakdown:
    """BudgetBreakdown 模型校验与自动计算测试."""

    def test_total_auto_calculated(self):
        """未提供 total 时自动计算."""
        budget = BudgetBreakdown(
            attraction_tickets=100,
            hotel_accommodation=200,
            dining_transport=150,
            dining_food=50,
        )
        assert budget.total == 500.0

    def test_total_auto_calculated_with_decimals(self):
        """自动计算支持小数."""
        budget = BudgetBreakdown(
            attraction_tickets=99.5,
            hotel_accommodation=199.99,
            dining_transport=50.0,
            dining_food=25.51,
        )
        assert budget.total == 375.0

    def test_explicit_total_preserved(self):
        """显式提供的 total 应保留（非零正数）."""
        budget = BudgetBreakdown(
            attraction_tickets=100,
            hotel_accommodation=200,
            dining_transport=150,
            dining_food=50,
            total=600,  # 故意设置不同的值
        )
        assert budget.total == 600

    def test_zero_total_triggers_recalculation(self):
        """total 为 0 时触发重新计算."""
        budget = BudgetBreakdown(
            attraction_tickets=100,
            hotel_accommodation=200,
            dining_transport=150,
            dining_food=50,
            total=0,
        )
        assert budget.total == 500.0

    def test_all_fields_present(self):
        """所有字段均应存在."""
        budget = BudgetBreakdown(
            attraction_tickets=100,
            hotel_accommodation=200,
            dining_transport=150,
            dining_food=50,
        )
        assert budget.attraction_tickets == 100
        assert budget.hotel_accommodation == 200
        assert budget.dining_transport == 150
        assert budget.dining_food == 50


class TestTimeSlot:
    """TimeSlot 模型校验测试."""

    def test_valid_time_slot(self):
        """有效时间段."""
        slot = TimeSlot(start_time="08:00", end_time="10:00", activity="游览故宫")
        assert slot.start_time == "08:00"
        assert slot.end_time == "10:00"

    def test_invalid_time_format(self):
        """无效时间格式应校验失败."""
        with pytest.raises(ValidationError):
            TimeSlot(start_time="8:00", end_time="10:00", activity="test")

    def test_missing_activity(self):
        """缺少 activity 应校验失败."""
        with pytest.raises(ValidationError):
            TimeSlot(start_time="08:00", end_time="10:00")


class TestAttractionDetail:
    """AttractionDetail 模型校验测试."""

    def test_minimal_valid(self):
        """最小有效创建（id 和 name 必填）."""
        attr = AttractionDetail(id="uuid-1", name="故宫")
        assert attr.id == "uuid-1"
        assert attr.name == "故宫"
        assert attr.image_url == ""
        assert attr.latitude == 0.0

    def test_full_valid(self):
        """完整有效创建."""
        attr = AttractionDetail(
            id="uuid-1",
            name="故宫",
            image_url="https://example.com/img.jpg",
            play_duration="2-3小时",
            description="皇家宫殿",
            features="世界文化遗产",
            tips="提前购票",
            latitude=39.9163,
            longitude=116.3972,
        )
        assert attr.play_duration == "2-3小时"

    def test_empty_name_raises_error(self):
        """空名称应校验失败."""
        with pytest.raises(ValidationError):
            AttractionDetail(id="uuid-1", name="")

    def test_missing_id_raises_error(self):
        """缺少 id 应校验失败."""
        with pytest.raises(ValidationError):
            AttractionDetail(name="故宫")


class TestAccommodationPlan:
    """AccommodationPlan 模型校验测试."""

    def test_all_defaults(self):
        """所有字段有默认值."""
        acc = AccommodationPlan()
        assert acc.hotel_name == ""
        assert acc.latitude == 0.0


class TestDiningPlan:
    """DiningPlan 模型校验测试."""

    def test_all_defaults(self):
        """所有字段有默认值."""
        dining = DiningPlan()
        assert dining.breakfast == ""
        assert dining.lunch == ""
        assert dining.dinner == ""


class TestTemperatureRange:
    """TemperatureRange 模型校验测试."""

    def test_valid_range(self):
        """有效温度范围."""
        temp = TemperatureRange(low=5, high=15)
        assert temp.low == 5
        assert temp.high == 15


class TestWeatherInfo:
    """WeatherInfo 模型校验测试."""

    def test_minimal_valid(self):
        """最小有效创建."""
        weather = WeatherInfo(date="2026-07-01", condition="晴")
        assert weather.wind_speed == "微风"
        assert weather.temperature is None

    def test_with_temperature(self):
        """含温度范围."""
        weather = WeatherInfo(
            date="2026-07-01",
            condition="晴",
            temperature=TemperatureRange(low=5, high=15),
        )
        assert weather.temperature.low == 5


class TestDailyItineraryDetail:
    """DailyItineraryDetail 模型校验测试."""

    def test_minimal_valid(self):
        """最小有效创建."""
        day = DailyItineraryDetail(
            day_index=1,
            date="2026-07-01",
            summary="一日游",
        )
        assert day.day_index == 1
        assert day.schedule == []
        assert day.attractions == []
        assert day.accommodation is None

    def test_day_index_range_validation(self):
        """day_index 超过 30 应校验失败."""
        with pytest.raises(ValidationError):
            DailyItineraryDetail(
                day_index=31,
                date="2026-07-01",
                summary="test",
            )

    def test_day_index_minimum(self):
        """day_index 小于 1 应校验失败."""
        with pytest.raises(ValidationError):
            DailyItineraryDetail(
                day_index=0,
                date="2026-07-01",
                summary="test",
            )

    def test_full_itinerary(self):
        """完整每日行程."""
        day = DailyItineraryDetail(
            day_index=1,
            date="2026-07-01",
            summary="故宫一日游",
            schedule=[
                TimeSlot(start_time="08:00", end_time="10:00", activity="前往故宫"),
            ],
            attractions=[
                AttractionDetail(id="a1", name="故宫"),
            ],
            accommodation=AccommodationPlan(hotel_name="万豪酒店"),
            dining=DiningPlan(breakfast="豆浆油条"),
            transportation=[
                TransportationPlan(type="地铁", description="1号线"),
            ],
            weather=WeatherInfo(date="2026-07-01", condition="晴"),
        )
        assert len(day.schedule) == 1
        assert len(day.attractions) == 1
        assert day.accommodation is not None
        assert day.dining is not None


class TestTravelPlanFull:
    """TravelPlanFull 模型校验测试."""

    def test_minimal_valid(self):
        """最小有效创建."""
        plan = TravelPlanFull(
            id="test-uuid",
            destination=DestinationCity(name="北京"),
            date_range=DateRange(
                start_date=date(2026, 7, 1),
                end_date=date(2026, 7, 15),
            ),
            budget=BudgetBreakdown(
                attraction_tickets=100,
                hotel_accommodation=200,
                dining_transport=50,
                dining_food=50,
            ),
            created_at="2026-06-01T10:00:00+08:00",
            updated_at="2026-06-01T10:00:00+08:00",
        )
        assert plan.id == "test-uuid"
        assert plan.daily_itineraries == []
        assert plan.description == ""
        assert plan.preferences is None

    def test_full_plan(self):
        """完整旅行计划."""
        plan = TravelPlanFull(
            id="test-uuid",
            destination=DestinationCity(name="北京", latitude=39.9042, longitude=116.4074),
            date_range=DateRange(
                start_date=date(2026, 7, 1),
                end_date=date(2026, 7, 15),
            ),
            description="15 天北京深度游",
            preferences=TravelPreferences(
                accommodation_type="高档型",
                transportation="高铁",
                tags=["景点观光"],
            ),
            budget=BudgetBreakdown(
                attraction_tickets=1130,
                hotel_accommodation=1200,
                dining_transport=730,
                dining_food=300,
            ),
            daily_itineraries=[
                DailyItineraryDetail(
                    day_index=1,
                    date="2026-07-01",
                    summary="故宫一日游",
                    schedule=[
                        TimeSlot(start_time="08:00", end_time="12:00", activity="游览故宫"),
                    ],
                    attractions=[
                        AttractionDetail(
                            id="a1",
                            name="故宫",
                            latitude=39.9163,
                            longitude=116.3972,
                        ),
                    ],
                ),
            ],
            created_at="2026-06-01T10:00:00+08:00",
            updated_at="2026-06-01T10:00:00+08:00",
        )
        assert len(plan.daily_itineraries) == 1
        assert plan.budget.total == 3360.0
        assert plan.destination.latitude == 39.9042

    def test_missing_required_fields(self):
        """缺少必填字段应校验失败."""
        with pytest.raises(ValidationError):
            TravelPlanFull(
                destination=DestinationCity(name="北京"),
                date_range=DateRange(
                    start_date=date(2026, 7, 1),
                    end_date=date(2026, 7, 15),
                ),
                budget=BudgetBreakdown(
                    attraction_tickets=100,
                    hotel_accommodation=200,
                    dining_transport=50,
                    dining_food=50,
                ),
                created_at="2026-06-01T10:00:00+08:00",
                updated_at="2026-06-01T10:00:00+08:00",
            )
