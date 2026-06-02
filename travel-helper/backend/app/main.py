"""FastAPI 应用入口."""

import uuid
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings

logger = logging.getLogger("travel-helper")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理."""
    logger.info(f"应用启动: {settings.app_env} 环境")
    yield
    logger.info("应用关闭")


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例."""
    app = FastAPI(
        title="旅行计划助手 API",
        description="智能旅行计划创建与管理",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 请求日志中间件
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        logger.info(f"请求开始: {request.method} {request.url.path} [req:{request_id}]")
        response = await call_next(request)
        logger.info(f"请求完成: {request.method} {request.url.path} -> {response.status_code} [req:{request_id}]")
        return response

    # 统一错误处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", "unknown")
        logger.error(f"未处理异常 [req:{request_id}]: {exc}")
        return JSONResponse(
            status_code=500,
            content={"request_id": request_id, "error": "服务器内部错误，请稍后重试"},
        )

    # 注册路由
    from app.api.routes.travel_plan import router as travel_plan_router

    app.include_router(travel_plan_router, prefix="/api/v1")

    return app


app = create_app()
