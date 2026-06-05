"""FastAPI 应用入口."""

import uuid
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import settings, apply_langsmith_settings

logger = logging.getLogger("travel-helper")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理."""
    logger.info(f"应用启动: {settings.app_env} 环境")
    apply_langsmith_settings()
    logger.info("LangSmith 配置已加载")
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
        allow_origins=["http://localhost:3000", "http://localhost:3001"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 请求日志中间件（结构化日志：请求 ID、时间戳、响应状态、耗时）
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        import time
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        start_time = time.time()
        timestamp = __import__("datetime").datetime.now().isoformat()

        logger.info(
            f"[{timestamp}] 请求开始: {request.method} {request.url.path} "
            f"[req:{request_id}] client={request.client.host if request.client else 'unknown'}"
        )

        response = await call_next(request)

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"[{timestamp}] 请求完成: {request.method} {request.url.path} "
            f"-> {response.status_code} [req:{request_id}] duration={duration_ms:.0f}ms"
        )

        return response

    # 请求校验错误统一格式
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        request_id = getattr(request.state, "request_id", "unknown")
        timestamp = __import__("datetime").datetime.now().isoformat()
        errors_summary = []
        for err in exc.errors():
            field = ".".join(str(loc) for loc in err.get("loc", []))
            errors_summary.append(f"{field}: {err.get('msg', '')}")
        detail = "; ".join(errors_summary)
        logger.warning(f"[{timestamp}] 请求校验失败 [req:{request_id}]: {detail}")
        return JSONResponse(
            status_code=422,
            content={"detail": detail},
        )

    # 统一错误处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        import traceback
        request_id = getattr(request.state, "request_id", "unknown")
        timestamp = __import__("datetime").datetime.now().isoformat()
        logger.error(
            f"[{timestamp}] 未处理异常 [req:{request_id}] "
            f"{request.method} {request.url.path}: {exc}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "服务器内部错误，请稍后重试",
                "request_id": request_id,
            },
        )

    # 注册路由
    from app.api.routes.travel_plan import router as travel_plan_router

    app.include_router(travel_plan_router, prefix="/api/v1")

    return app


app = create_app()
