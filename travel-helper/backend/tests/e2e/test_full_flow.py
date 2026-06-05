"""端到端集成测试 — 完整用户旅程: 创建 -> 概览 -> 详情 -> 编辑 -> 导出.

覆盖用户从创建旅行计划到导出的完整流程。
"""

import pytest
from datetime import date, timedelta
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.travel_plan_service import _plans, TravelPlanFull
from app.models.travel_plan import (
    DestinationCity,
    DateRange,
    TravelPreferences,
    BudgetBreakdown,
    DailyItineraryDetail,
    TimeSlot,
    AttractionDetail,
    AccommodationPlan,
    DiningPlan,
    TransportationPlan,
    WeatherInfo,
    TemperatureRange,
)


@pytest.fixture
async def client():
    """创建异步 HTTP 客户端."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def seed_test_plan():
    """创建一个包含完整数据的测试计划并写入内存存储.

    该计划包含 2 天行程，每有多个景点、住宿、餐饮、交通和天气数据，
    用于端到端测试的初始数据。
    """
    plan_id = "e2e-test-plan-001"

    budget = BudgetBreakdown(
        attraction_tickets=1130,
        hotel_accommodation=1200,
        dining_transport=730,
        dining_food=300,
        total=3360,
    )

    daily_itineraries = [
        # 第 1 天
        DailyItineraryDetail(
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
                    id="e2e-uuid-1",
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
                    id="e2e-uuid-2",
                    name="国家体育场（鸟巢）",
                    image_url="",
                    play_duration="1-2小时",
                    description="2008年北京奥运会主体育场",
                    features="标志性建筑",
                    tips="夜间灯光效果更佳",
                    latitude=39.9928,
                    longitude=116.3973,
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
                TransportationPlan(type="地铁", description="地铁1号线 天安门东站 → 奥林匹克公园站"),
            ],
            weather=WeatherInfo(
                date="2026-07-01",
                condition="晴",
                temperature=TemperatureRange(low=22, high=32),
                wind_speed="微风",
            ),
        ),
        # 第 2 天
        DailyItineraryDetail(
            day_index=2,
            date="2026-07-02",
            summary="颐和园 - 圆明园",
            schedule=[
                TimeSlot(start_time="08:00", end_time="12:00", activity="游览颐和园"),
                TimeSlot(start_time="13:00", end_time="16:00", activity="游览圆明园"),
            ],
            attractions=[
                AttractionDetail(
                    id="e2e-uuid-3",
                    name="颐和园",
                    image_url="",
                    play_duration="3-4小时",
                    description="中国古典园林之首",
                    features="世界文化遗产",
                    tips="",
                    latitude=39.9985,
                    longitude=116.2745,
                ),
            ],
            accommodation=None,
            dining=DiningPlan(
                breakfast="酒店自助早餐",
                lunch="园区附近简餐",
                dinner="返回市区用餐",
            ),
            transportation=[
                TransportationPlan(type="地铁", description="地铁4号线"),
            ],
            weather=WeatherInfo(
                date="2026-07-02",
                condition="多云",
                temperature=TemperatureRange(low=20, high=30),
                wind_speed="2级",
            ),
        ),
    ]

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
        description="北京5日游旅行计划 — E2E 测试",
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


class TestEndToEndFlow:
    """端到端完整用户旅程测试.

    流程: 创建 -> 概览(GET) -> 详情(GET day) -> 编辑(PUT day) -> 导出(GET export)
    """

    # -------------------------------------------------------------------------
    # Step 1: 创建旅行计划（通过写入内存存储模拟）
    # -------------------------------------------------------------------------

    async def test_step1_plan_exists(self, seed_test_plan):
        """种子计划已成功写入内存存储."""
        assert seed_test_plan in _plans
        plan = _plans[seed_test_plan]
        assert plan.destination.name == "北京"
        assert len(plan.daily_itineraries) == 2

    # -------------------------------------------------------------------------
    # Step 2: 获取概览页数据
    # -------------------------------------------------------------------------

    async def test_step2_get_overview(self, client, seed_test_plan):
        """GET /travel-plans/{id} 返回完整概览数据."""
        response = await client.get(f"/api/v1/travel-plans/{seed_test_plan}")
        assert response.status_code == 200

        data = response.json()
        # 验证顶层字段
        assert data["id"] == seed_test_plan
        assert data["destination"]["name"] == "北京"
        assert "dateRange" in data
        assert "budget" in data
        assert "preferences" in data
        assert "dailyItineraries" in data
        assert "createdAt" in data
        assert "updatedAt" in data

        # 验证预算数据
        budget = data["budget"]
        assert budget["total"] == 3360
        assert budget["attractionTickets"] == 1130

        # 验证偏好数据
        prefs = data["preferences"]
        assert prefs["accommodationType"] == "高档型酒店"
        assert prefs["transportation"] == "高铁"

    async def test_step2_overview_daily_list(self, client, seed_test_plan):
        """概览页包含完整的每日行程列表."""
        response = await client.get(f"/api/v1/travel-plans/{seed_test_plan}")
        data = response.json()

        itineraries = data["dailyItineraries"]
        assert len(itineraries) == 2
        assert itineraries[0]["dayIndex"] == 1
        assert itineraries[0]["summary"] == "故宫 - 鸟巢一日游"
        assert itineraries[1]["dayIndex"] == 2
        assert itineraries[1]["summary"] == "颐和园 - 圆明园"

    # -------------------------------------------------------------------------
    # Step 3: 获取逐日详情页数据
    # -------------------------------------------------------------------------

    async def test_step3_get_day_detail(self, client, seed_test_plan):
        """GET /travel-plans/{id}/day/1 返回第1天完整详情."""
        response = await client.get(f"/api/v1/travel-plans/{seed_test_plan}/day/1")
        assert response.status_code == 200

        data = response.json()
        assert data["dayIndex"] == 1
        assert data["date"] == "2026-07-01"
        assert len(data["attractions"]) == 2
        assert data["attractions"][0]["name"] == "北京故宫"

        # 验证住宿
        assert data["accommodation"]["hotelName"] == "北京万豪酒店"
        # 验证餐饮
        assert data["dining"]["breakfast"] == "北京传统早餐"
        # 验证交通
        assert len(data["transportation"]) == 1
        # 验证天气
        assert data["weather"]["condition"] == "晴"
        assert data["weather"]["temperature"]["low"] == 22

    async def test_step3_get_day_detail_day2(self, client, seed_test_plan):
        """GET /travel-plans/{id}/day/2 返回第2天完整详情."""
        response = await client.get(f"/api/v1/travel-plans/{seed_test_plan}/day/2")
        assert response.status_code == 200

        data = response.json()
        assert data["dayIndex"] == 2
        assert len(data["attractions"]) == 1
        assert data["attractions"][0]["name"] == "颐和园"

    # -------------------------------------------------------------------------
    # Step 4: 编辑行程
    # -------------------------------------------------------------------------

    async def test_step4_edit_day1(self, client, seed_test_plan):
        """PUT /travel-plans/{id}/day/1 编辑第1天行程."""
        payload = {
            "schedule": [
                {"startTime": "09:00", "endTime": "11:30", "activity": "游览故宫（已编辑）"},
                {"startTime": "14:00", "endTime": "16:00", "activity": "游览鸟巢（已编辑）"},
            ],
            "attractions": [
                {
                    "id": "e2e-uuid-1",
                    "name": "北京故宫",
                    "imageUrl": "https://images.unsplash.com/forbidden-city-edited",
                    "playDuration": "3小时",
                    "description": "更新后的描述",
                    "features": "世界文化遗产（编辑）",
                    "tips": "建议提前网上购票",
                    "latitude": 39.9163,
                    "longitude": 116.3972,
                },
                {
                    "id": "e2e-uuid-2",
                    "name": "国家体育场（鸟巢）",
                    "imageUrl": "",
                    "playDuration": "1.5小时",
                    "description": "",
                    "features": "",
                    "tips": "",
                    "latitude": 39.9928,
                    "longitude": 116.3973,
                },
            ],
            "dining": {
                "breakfast": "酒店自助早餐（编辑）",
                "lunch": "故宫附近餐厅",
                "dinner": "北京烤鸭（编辑）",
            },
        }

        response = await client.put(
            f"/api/v1/travel-plans/{seed_test_plan}/day/1",
            json=payload,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Day itinerary updated successfully"
        assert data["dayIndex"] == 1
        assert "updatedAt" in data

    async def test_step4_edit_persisted(self, client, seed_test_plan):
        """编辑后的数据应被持久化，GET 时应返回更新后的值.

        本测试独立执行编辑和验证，不依赖其他测试。
        """
        # 先执行编辑
        payload = {
            "schedule": [
                {"startTime": "09:00", "endTime": "11:30", "activity": "验证持久性测试"},
            ],
            "attractions": [
                {
                    "id": "e2e-uuid-1",
                    "name": "北京故宫",
                    "imageUrl": "",
                    "playDuration": "2小时",
                    "description": "持久性验证描述",
                    "features": "",
                    "tips": "",
                    "latitude": 39.9163,
                    "longitude": 116.3972,
                },
            ],
        }

        response = await client.put(
            f"/api/v1/travel-plans/{seed_test_plan}/day/1",
            json=payload,
        )
        assert response.status_code == 200

        # GET 验证更新
        response = await client.get(f"/api/v1/travel-plans/{seed_test_plan}/day/1")
        assert response.status_code == 200
        data = response.json()

        # 验证景点描述已更新
        assert data["attractions"][0]["description"] == "持久性验证描述"
        # 验证日程已更新
        assert data["schedule"][0]["activity"] == "验证持久性测试"

    async def test_step4_edit_invalid_zero_attractions(self, client, seed_test_plan):
        """编辑时景点数为 0 应返回 400."""
        payload = {
            "schedule": [
                {"startTime": "09:00", "endTime": "12:00", "activity": "自由活动"},
            ],
            "attractions": [],  # 空景点
        }

        response = await client.put(
            f"/api/v1/travel-plans/{seed_test_plan}/day/1",
            json=payload,
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "至少保留 1 个景点" in data["detail"]

    # -------------------------------------------------------------------------
    # Step 5: 导出旅行计划
    # -------------------------------------------------------------------------

    async def test_step5_export_text(self, client, seed_test_plan):
        """GET /travel-plans/{id}/export?fmt=text 返回纯文本导出."""
        response = await client.get(
            f"/api/v1/travel-plans/{seed_test_plan}/export?fmt=text"
        )
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")

        content = response.text
        assert "北京" in content
        assert "故宫" in content
        assert "预算明细" in content
        assert "3360" in content
        assert "第 1 天" in content
        assert "第 2 天" in content

    async def test_step5_export_html(self, client, seed_test_plan):
        """GET /travel-plans/{id}/export?fmt=html 返回 HTML 导出."""
        response = await client.get(
            f"/api/v1/travel-plans/{seed_test_plan}/export?fmt=html"
        )
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

        content = response.text
        assert "<!DOCTYPE html>" in content
        assert "北京" in content
        assert "故宫" in content
        assert "预算明细" in content

    async def test_step5_export_invalid_format(self, client, seed_test_plan):
        """导出格式无效应返回 400."""
        response = await client.get(
            f"/api/v1/travel-plans/{seed_test_plan}/export?fmt=pdf"
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Invalid format" in data["detail"]

    async def test_step5_export_nonexistent_plan(self, client):
        """导出不存在的计划应返回 404."""
        response = await client.get("/api/v1/travel-plans/nonexistent-id/export?fmt=text")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    # -------------------------------------------------------------------------
    # Full flow validation
    # -------------------------------------------------------------------------

    async def test_full_flow_integration(self, client, seed_test_plan):
        """完整用户旅程集成测试.

        按顺序执行: 概览 -> 详情 -> 编辑 -> 再次详情 -> 导出
        确保每个环节的数据传递正确。
        """
        # 1. 获取概览
        overview = await client.get(f"/api/v1/travel-plans/{seed_test_plan}")
        assert overview.status_code == 200
        overview_data = overview.json()
        assert len(overview_data["dailyItineraries"]) == 2

        # 2. 查看第1天详情
        day1_before = await client.get(f"/api/v1/travel-plans/{seed_test_plan}/day/1")
        assert day1_before.status_code == 200
        day1_before_data = day1_before.json()
        original_attraction_name = day1_before_data["attractions"][0]["name"]

        # 3. 编辑第1天
        edit_payload = {
            "schedule": day1_before_data["schedule"],
            "attractions": [
                {
                    **day1_before_data["attractions"][0],
                    "name": "北京故宫（E2E编辑）",
                },
            ],
        }
        edit_response = await client.put(
            f"/api/v1/travel-plans/{seed_test_plan}/day/1",
            json=edit_payload,
        )
        assert edit_response.status_code == 200

        # 4. 再次查看第1天，确认编辑生效
        day1_after = await client.get(f"/api/v1/travel-plans/{seed_test_plan}/day/1")
        assert day1_after.status_code == 200
        day1_after_data = day1_after.json()
        assert day1_after_data["attractions"][0]["name"] == "北京故宫（E2E编辑）"

        # 5. 导出
        export_response = await client.get(
            f"/api/v1/travel-plans/{seed_test_plan}/export?fmt=text"
        )
        assert export_response.status_code == 200
        # 导出内容应包含更新后的景点名称
        assert "北京故宫（E2E编辑）" in export_response.text

        # 6. 验证概览页 updatedAt 已更新
        overview_after = await client.get(f"/api/v1/travel-plans/{seed_test_plan}")
        assert overview_after.status_code == 200
        overview_after_data = overview_after.json()
        # updatedAt 应该在编辑后被更新
        assert overview_after_data["updatedAt"] != overview_data.get("createdAt")
