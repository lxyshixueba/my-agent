"""编辑每日行程校验规则单元测试.

验证 update_day_itinerary 的校验规则：
- 至少保留 1 个景点（FR-013）
- dayIndex 范围校验
- 计划不存在时抛出 KeyError
- 指定天不存在时抛出 KeyError
"""

import pytest
from datetime import date
from app.models.travel_plan import (
    EditDayRequest,
    AttractionDetail,
    TimeSlot,
    DestinationCity,
    DateRange,
    TravelPreferences,
    BudgetBreakdown,
    DailyItineraryDetail,
    AccommodationPlan,
    DiningPlan,
    TransportationPlan,
    WeatherInfo,
    TemperatureRange,
    TravelPlanFull,
)
from app.services.travel_plan_service import (
    _plans,
    update_day_itinerary,
    EditDayValidationError,
)


@pytest.fixture(autouse=True)
def cleanup_plans():
    """每个测试后清理全局状态."""
    yield
    _plans.clear()


@pytest.fixture
def sample_plan():
    """创建一个包含 3 天行程的样本计划并写入内存存储."""
    plan_id = "test-edit-day-plan-001"

    budget = BudgetBreakdown(
        attraction_tickets=3390,
        hotel_accommodation=3600,
        dining_transport=2190,
        dining_food=900,
        total=10080,
    )

    daily_itineraries = []

    # 第 1 天 — 3 个景点
    day1 = DailyItineraryDetail(
        day_index=1,
        date="2026-07-01",
        summary="故宫 - 鸟巢一日游",
        schedule=[
            TimeSlot(start_time="08:00", end_time="10:00", activity="前往故宫并游览"),
            TimeSlot(start_time="10:30", end_time="12:00", activity="继续游览故宫"),
            TimeSlot(start_time="13:00", end_time="15:00", activity="前往鸟巢游览"),
        ],
        attractions=[
            AttractionDetail(
                id="uuid-1",
                name="北京故宫",
                image_url="https://images.unsplash.com/forbidden-city",
                play_duration="2-3小时",
                description="中国明清两代的皇家宫殿",
                features="世界文化遗产",
                tips="建议提前网上购票",
                latitude=39.9163,
                longitude=116.3972,
            ),
            AttractionDetail(
                id="uuid-2",
                name="国家体育场（鸟巢）",
                image_url="https://images.unsplash.com/birds-nest",
                play_duration="1-2小时",
                description="2008年北京奥运会主体育场",
                features="标志性建筑",
                tips="夜间灯光效果更佳",
                latitude=39.9928,
                longitude=116.3973,
            ),
            AttractionDetail(
                id="uuid-3",
                name="水立方",
                image_url="",
                play_duration="1小时",
                description="国家游泳中心",
                features="奥运场馆",
                tips="",
                latitude=39.9930,
                longitude=116.3975,
            ),
        ],
        accommodation=AccommodationPlan(
            hotel_name="北京万豪酒店",
            room_type="豪华标准间",
            address="北京市朝阳区xxx路xxx号",
            check_in="2026-07-01",
            check_out="2026-07-03",
            amenities="免费WiFi、停车位",
            latitude=39.9200,
            longitude=116.4100,
        ),
        dining=DiningPlan(
            breakfast="北京传统早餐",
            lunch="北京烤鸭",
            dinner="北京炸酱面",
        ),
        transportation=[
            TransportationPlan(type="地铁", description="地铁1号线"),
        ],
        weather=WeatherInfo(
            date="2026-07-01",
            condition="晴",
            temperature=TemperatureRange(low=22, high=32),
            wind_speed="微风",
        ),
    )
    daily_itineraries.append(day1)

    # 第 2 天 — 1 个景点（最少数量）
    day2 = DailyItineraryDetail(
        day_index=2,
        date="2026-07-02",
        summary="长城一日游",
        schedule=[
            TimeSlot(start_time="07:00", end_time="09:00", activity="乘车前往八达岭长城"),
            TimeSlot(start_time="09:00", end_time="13:00", activity="游览八达岭长城"),
        ],
        attractions=[
            AttractionDetail(
                id="uuid-4",
                name="八达岭长城",
                image_url="",
                play_duration="3-4小时",
                description="万里长城的精华段落",
                features="世界文化遗产",
                tips="建议穿舒适的运动鞋",
                latitude=40.3545,
                longitude=116.0137,
            ),
        ],
        accommodation=None,
        dining=DiningPlan(
            breakfast="酒店自助早餐",
            lunch="农家菜",
            dinner="王府井小吃",
        ),
        transportation=[
            TransportationPlan(type="大巴", description="877路公交车"),
        ],
        weather=WeatherInfo(
            date="2026-07-02",
            condition="多云",
            temperature=TemperatureRange(low=20, high=30),
            wind_speed="3级",
        ),
    )
    daily_itineraries.append(day2)

    # 第 3 天 — 2 个景点
    day3 = DailyItineraryDetail(
        day_index=3,
        date="2026-07-03",
        summary="颐和园 - 圆明园",
        schedule=[
            TimeSlot(start_time="08:00", end_time="12:00", activity="游览颐和园"),
            TimeSlot(start_time="13:00", end_time="16:00", activity="游览圆明园"),
        ],
        attractions=[
            AttractionDetail(
                id="uuid-5",
                name="颐和园",
                image_url="",
                play_duration="3-4小时",
                description="中国古典园林之首",
                features="世界文化遗产",
                tips="",
                latitude=39.9985,
                longitude=116.2745,
            ),
            AttractionDetail(
                id="uuid-6",
                name="圆明园",
                image_url="",
                play_duration="2-3小时",
                description="万园之园",
                features="历史遗迹",
                tips="",
                latitude=40.0083,
                longitude=116.2983,
            ),
        ],
        accommodation=None,
        dining=DiningPlan(
            breakfast="酒店早餐",
            lunch="园区附近简餐",
            dinner="返回市区用餐",
        ),
        transportation=[
            TransportationPlan(type="地铁", description="地铁4号线"),
        ],
        weather=WeatherInfo(
            date="2026-07-03",
            condition="晴",
            temperature=TemperatureRange(low=21, high=31),
            wind_speed="微风",
        ),
    )
    daily_itineraries.append(day3)

    plan = TravelPlanFull(
        id=plan_id,
        destination=DestinationCity(
            name="北京",
            latitude=39.9042,
            longitude=116.4074,
        ),
        date_range=DateRange(
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 5),
        ),
        description="北京5日游旅行计划",
        preferences=TravelPreferences(
            accommodation_type="高档型酒店",
            transportation="高铁",
            tags=["景点观光", "美食"],
            special_requests="",
        ),
        budget=budget,
        daily_itineraries=daily_itineraries,
        created_at="2026-06-01T10:00:00+08:00",
        updated_at="2026-06-01T10:00:00+08:00",
    )

    _plans[plan_id] = plan
    return plan_id


class TestEditDayAttractionValidation:
    """编辑行程景点数量校验测试."""

    def test_remove_all_attractions_raises_error(self, sample_plan):
        """删除全部景点（0 个）应抛出 EditDayValidationError."""
        request = EditDayRequest(
            schedule=[
                TimeSlot(start_time="08:00", end_time="10:00", activity="自由活动"),
            ],
            attractions=[],  # 空景点列表
            accommodation=None,
            dining=None,
            transportation=[],
        )

        with pytest.raises(EditDayValidationError) as exc_info:
            update_day_itinerary(sample_plan, 1, request)

        assert "至少保留 1 个景点" in str(exc_info.value)

    def test_keep_one_attraction_succeeds(self, sample_plan):
        """保留 1 个景点应该成功."""
        request = EditDayRequest(
            schedule=[
                TimeSlot(start_time="08:00", end_time="12:00", activity="游览八达岭长城"),
            ],
            attractions=[
                AttractionDetail(
                    id="uuid-4",
                    name="八达岭长城",
                    image_url="",
                    play_duration="3-4小时",
                    description="万里长城的精华段落",
                    features="世界文化遗产",
                    tips="",
                    latitude=40.3545,
                    longitude=116.0137,
                ),
            ],
            accommodation=None,
            dining=None,
            transportation=[],
        )

        # 不应抛出异常
        updated_at = update_day_itinerary(sample_plan, 2, request)
        assert updated_at is not None
        assert isinstance(updated_at, str)

    def test_keep_multiple_attractions_succeeds(self, sample_plan):
        """保留多个景点应该成功."""
        request = EditDayRequest(
            schedule=[
                TimeSlot(start_time="08:00", end_time="10:00", activity="前往故宫并游览"),
                TimeSlot(start_time="10:30", end_time="12:00", activity="继续游览故宫"),
            ],
            attractions=[
                AttractionDetail(
                    id="uuid-1",
                    name="北京故宫",
                    image_url="https://images.unsplash.com/forbidden-city",
                    play_duration="2-3小时",
                    description="中国明清两代的皇家宫殿",
                    features="世界文化遗产",
                    tips="",
                    latitude=39.9163,
                    longitude=116.3972,
                ),
                AttractionDetail(
                    id="uuid-2",
                    name="国家体育场（鸟巢）",
                    image_url="https://images.unsplash.com/birds-nest",
                    play_duration="1-2小时",
                    description="2008年北京奥运会主体育场",
                    features="标志性建筑",
                    tips="",
                    latitude=39.9928,
                    longitude=116.3973,
                ),
            ],
            accommodation=None,
            dining=None,
            transportation=[],
        )

        updated_at = update_day_itinerary(sample_plan, 1, request)
        assert updated_at is not None


class TestEditDayPlanValidation:
    """编辑行程计划存在性校验测试."""

    def test_nonexistent_plan_raises_key_error(self):
        """不存在的计划 ID 应抛出 KeyError."""
        request = EditDayRequest(
            attractions=[
                AttractionDetail(
                    id="uuid-1",
                    name="故宫",
                    image_url="",
                    play_duration="2小时",
                    description="",
                    features="",
                    tips="",
                    latitude=0.0,
                    longitude=0.0,
                ),
            ],
        )

        with pytest.raises(KeyError):
            update_day_itinerary("nonexistent-plan-id", 1, request)

    def test_nonexistent_day_raises_key_error(self, sample_plan):
        """不存在的 dayIndex 应抛出 KeyError."""
        request = EditDayRequest(
            attractions=[
                AttractionDetail(
                    id="uuid-1",
                    name="故宫",
                    image_url="",
                    play_duration="2小时",
                    description="",
                    features="",
                    tips="",
                    latitude=0.0,
                    longitude=0.0,
                ),
            ],
        )

        with pytest.raises(KeyError):
            update_day_itinerary(sample_plan, 10, request)


class TestEditDayDayIndexValidation:
    """编辑行程 dayIndex 范围校验测试."""

    def test_day_index_out_of_range_raises_error(self, sample_plan):
        """dayIndex 超过 30 应抛出 EditDayValidationError."""
        request = EditDayRequest(
            attractions=[
                AttractionDetail(
                    id="uuid-1",
                    name="故宫",
                    image_url="",
                    play_duration="2小时",
                    description="",
                    features="",
                    tips="",
                    latitude=0.0,
                    longitude=0.0,
                ),
            ],
        )

        with pytest.raises(EditDayValidationError) as exc_info:
            update_day_itinerary(sample_plan, 31, request)

        assert "1-30" in str(exc_info.value)

    def test_day_index_zero_raises_error(self, sample_plan):
        """dayIndex 为 0 应抛出 EditDayValidationError."""
        request = EditDayRequest(
            attractions=[
                AttractionDetail(
                    id="uuid-1",
                    name="故宫",
                    image_url="",
                    play_duration="2小时",
                    description="",
                    features="",
                    tips="",
                    latitude=0.0,
                    longitude=0.0,
                ),
            ],
        )

        with pytest.raises(EditDayValidationError):
            update_day_itinerary(sample_plan, 0, request)


class TestEditDayUpdateBehavior:
    """编辑行程更新行为测试."""

    def test_update_changes_attractions(self, sample_plan):
        """更新后景点列表应与请求一致."""
        new_attraction = AttractionDetail(
            id="uuid-new",
            name="天坛公园",
            image_url="",
            play_duration="2小时",
            description="明清两代皇帝祭天的场所",
            features="世界文化遗产",
            tips="",
            latitude=39.8822,
            longitude=116.4066,
        )

        request = EditDayRequest(
            schedule=[
                TimeSlot(start_time="09:00", end_time="12:00", activity="游览天坛公园"),
            ],
            attractions=[new_attraction],
            accommodation=None,
            dining=None,
            transportation=[],
        )

        update_day_itinerary(sample_plan, 3, request)

        # 验证存储中的数据已更新
        plan = _plans[sample_plan]
        day3 = None
        for day in plan.daily_itineraries:
            if day.day_index == 3:
                day3 = day
                break

        assert day3 is not None
        assert len(day3.attractions) == 1
        assert day3.attractions[0].name == "天坛公园"
        assert day3.attractions[0].id == "uuid-new"

    def test_update_changes_schedule(self, sample_plan):
        """更新后时间线应与请求一致."""
        new_schedule = [
            TimeSlot(start_time="06:00", end_time="08:00", activity="早起出发"),
            TimeSlot(start_time="08:00", end_time="14:00", activity="全天游览"),
        ]

        request = EditDayRequest(
            schedule=new_schedule,
            attractions=[
                AttractionDetail(
                    id="uuid-5",
                    name="颐和园",
                    image_url="",
                    play_duration="3-4小时",
                    description="",
                    features="",
                    tips="",
                    latitude=39.9985,
                    longitude=116.2745,
                ),
            ],
        )

        update_day_itinerary(sample_plan, 3, request)

        plan = _plans[sample_plan]
        day3 = next((d for d in plan.daily_itineraries if d.day_index == 3), None)
        assert day3 is not None
        assert len(day3.schedule) == 2
        assert day3.schedule[0].start_time == "06:00"
        assert day3.schedule[1].activity == "全天游览"

    def test_update_preserves_other_days(self, sample_plan):
        """更新某天不应影响其他天的数据."""
        # 记录第 1 天的原始景点数量
        plan = _plans[sample_plan]
        day1_original_attractions_count = len(
            next(d for d in plan.daily_itineraries if d.day_index == 1).attractions
        )

        # 更新第 3 天
        request = EditDayRequest(
            schedule=[
                TimeSlot(start_time="09:00", end_time="12:00", activity="游览"),
            ],
            attractions=[
                AttractionDetail(
                    id="uuid-new",
                    name="新景点",
                    image_url="",
                    play_duration="2小时",
                    description="",
                    features="",
                    tips="",
                    latitude=0.0,
                    longitude=0.0,
                ),
            ],
        )

        update_day_itinerary(sample_plan, 3, request)

        # 验证第 1 天未受影响
        day1 = next(d for d in plan.daily_itineraries if d.day_index == 1)
        assert len(day1.attractions) == day1_original_attractions_count

    def test_update_updates_timestamp(self, sample_plan):
        """更新后 updatedAt 时间戳应被更新."""
        plan = _plans[sample_plan]
        original_updated_at = plan.updated_at

        request = EditDayRequest(
            schedule=[
                TimeSlot(start_time="09:00", end_time="12:00", activity="游览"),
            ],
            attractions=[
                AttractionDetail(
                    id="uuid-1",
                    name="故宫",
                    image_url="",
                    play_duration="2小时",
                    description="",
                    features="",
                    tips="",
                    latitude=0.0,
                    longitude=0.0,
                ),
            ],
        )

        updated_at = update_day_itinerary(sample_plan, 1, request)

        # updatedAt 已更新且与返回的值一致
        assert plan.updated_at == updated_at
        assert updated_at != original_updated_at

    def test_update_returns_iso_timestamp(self, sample_plan):
        """返回的 updatedAt 应为 ISO 8601 格式时间戳."""
        import re

        request = EditDayRequest(
            schedule=[
                TimeSlot(start_time="09:00", end_time="12:00", activity="游览"),
            ],
            attractions=[
                AttractionDetail(
                    id="uuid-1",
                    name="故宫",
                    image_url="",
                    play_duration="2小时",
                    description="",
                    features="",
                    tips="",
                    latitude=0.0,
                    longitude=0.0,
                ),
            ],
        )

        updated_at = update_day_itinerary(sample_plan, 1, request)

        # ISO 8601 格式检查（包含 +08:00 时区）
        iso_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
        assert re.match(iso_pattern, updated_at) is not None

    def test_update_with_accommodation_and_dining(self, sample_plan):
        """更新时同时修改住宿和餐饮安排."""
        request = EditDayRequest(
            schedule=[
                TimeSlot(start_time="09:00", end_time="12:00", activity="游览"),
            ],
            attractions=[
                AttractionDetail(
                    id="uuid-5",
                    name="颐和园",
                    image_url="",
                    play_duration="3小时",
                    description="",
                    features="",
                    tips="",
                    latitude=39.9985,
                    longitude=116.2745,
                ),
            ],
            accommodation=AccommodationPlan(
                hotel_name="颐和园附近酒店",
                room_type="标准间",
                address="海淀区xxx路",
                check_in="2026-07-03",
                check_out="2026-07-04",
                amenities="免费WiFi",
                latitude=39.9985,
                longitude=116.2745,
            ),
            dining=DiningPlan(
                breakfast="酒店早餐",
                lunch="颐和园附近餐厅",
                dinner="返回市区用餐",
            ),
            transportation=[
                TransportationPlan(type="公交", description="公交332路"),
            ],
        )

        update_day_itinerary(sample_plan, 3, request)

        plan = _plans[sample_plan]
        day3 = next(d for d in plan.daily_itineraries if d.day_index == 3)

        assert day3.accommodation is not None
        assert "颐和园附近酒店" in day3.accommodation.hotel_name
        assert day3.dining is not None
        assert "颐和园附近餐厅" in day3.dining.lunch
        assert len(day3.transportation) == 1
        assert day3.transportation[0].type == "公交"
