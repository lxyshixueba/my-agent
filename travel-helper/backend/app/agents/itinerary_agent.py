"""行程规划智能体 — LangGraph StateGraph 重新规划流程.

实现基于 LangGraph 的行程重新规划流程，包含三个节点：
- collect_context: 收集当前行程上下文、用户编辑痕迹、新约束
- call_llm: 调用 LLM 生成新行程
- return_result: 返回新行程结果

LangSmith 追踪: 当 LANGSMITH_TRACING=true 且 LANGSMITH_API_KEY 已配置时，
所有 LLM 调用和 StateGraph 执行将被自动追踪到 LangSmith 平台。
"""

import json
import logging
import os
from typing import Any, Optional

from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from app.config import settings
from app.templates.travel_planner.replan import REPLAN_SYSTEM_PROMPT, build_replan_user_prompt

logger = logging.getLogger("travel-helper")


# =============================================================================
# State 定义
# =============================================================================


class ReplanState(BaseModel):
    """重新规划流程的状态."""

    # 输入参数
    plan_id: str = Field(default="", description="旅行计划 ID")
    destination: str = Field(default="", description="目的地城市")
    days: int = Field(default=1, description="出行天数")
    start_date: str = Field(default="", description="出发日期")
    end_date: str = Field(default="", description="返回日期")
    transport: str = Field(default="", description="交通方式")
    accommodation: str = Field(default="", description="住宿偏好")
    preferences: list[str] = Field(default_factory=list, description="偏好标签")
    special_requests: str = Field(default="", description="特殊要求")

    # 可选上下文
    current_itinerary: str = Field(default="", description="当前行程 JSON")
    edit_traces: str = Field(default="", description="用户编辑痕迹")
    new_constraints: str = Field(default="", description="新增约束条件")

    # 输出
    llm_response: str = Field(default="", description="LLM 生成的行程 JSON")
    result: Optional[dict[str, Any]] = Field(default=None, description="解析后的结果")
    error: Optional[str] = Field(default=None, description="错误信息")


# =============================================================================
# 节点函数
# =============================================================================


def collect_context(state: ReplanState) -> dict[str, Any]:
    """收集上下文节点.

    验证必要输入参数是否完整，准备传递给 LLM 的上下文信息。

    Args:
        state: 当前状态

    Returns:
        状态更新字典
    """
    logger.info(f"[replan:collect_context] 收集行程上下文 [plan:{state.plan_id}]")

    # 验证必要参数
    missing = []
    if not state.destination:
        missing.append("destination")
    if state.days < 1:
        missing.append("days")
    if not state.start_date:
        missing.append("start_date")
    if not state.end_date:
        missing.append("end_date")

    if missing:
        error_msg = f"缺少必要参数: {', '.join(missing)}"
        logger.error(f"[replan:collect_context] {error_msg}")
        return {"error": error_msg}

    context_info = {
        "destination": state.destination,
        "days": state.days,
        "date_range": f"{state.start_date} ~ {state.end_date}",
        "transport": state.transport,
        "accommodation": state.accommodation,
    }
    logger.info(f"[replan:collect_context] 上下文收集完成: {context_info}")

    return {"error": None}


async def call_llm(state: ReplanState) -> dict[str, Any]:
    """调用 LLM 节点.

    使用 LangChain ChatOpenAI 调用 LLM，生成重新规划的行程。
    LangSmith 会自动追踪此调用（当 LANGSMITH_TRACING=true 时）。

    Args:
        state: 当前状态

    Returns:
        状态更新字典，包含 llm_response 或 error
    """
    logger.info(f"[replan:call_llm] 开始调用 LLM [plan:{state.plan_id}]")

    try:
        # 动态导入 LangChain（避免未安装时的导入错误）
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_core.callbacks import CallbackManager

        # LangSmith 回调：如果追踪已开启，自动记录 LLM 调用
        use_tracing = (
            os.environ.get("LANGSMITH_TRACING") == "true"
            and os.environ.get("LANGSMITH_API_KEY")
        )

        callback_manager = None
        if use_tracing:
            try:
                from langsmith import traceable
                logger.info(f"[replan:call_llm] LangSmith 追踪已启用")
            except ImportError:
                logger.warning("[replan:call_llm] langsmith 未安装，追踪不可用")

        # 初始化 LLM
        llm = ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            base_url=settings.llm_api_base_url,
            temperature=0.7,
            timeout=settings.llm_timeout,
            max_retries=settings.llm_max_retries,
            # LangSmith 自动追踪通过环境变量激活
        )

        # 构建 prompt
        system_prompt = REPLAN_SYSTEM_PROMPT
        user_prompt = build_replan_user_prompt(
            destination=state.destination,
            days=state.days,
            start_date=state.start_date,
            end_date=state.end_date,
            transport=state.transport,
            accommodation=state.accommodation,
            preferences=state.preferences if state.preferences else None,
            special_requests=state.special_requests if state.special_requests else None,
            current_itinerary=state.current_itinerary if state.current_itinerary else None,
            edit_traces=state.edit_traces if state.edit_traces else None,
            new_constraints=state.new_constraints if state.new_constraints else None,
        )

        # 调用 LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        response = await llm.ainvoke(messages)
        llm_response = response.content

        logger.info(f"[replan:call_llm] LLM 调用成功，响应长度: {len(llm_response)} 字符")

        return {"llm_response": llm_response, "error": None}

    except ImportError as e:
        error_msg = f"LangChain 未安装: {e}"
        logger.error(f"[replan:call_llm] {error_msg}")
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"LLM 调用失败: {e}"
        logger.error(f"[replan:call_llm] {error_msg}")
        return {"error": error_msg}


def return_result(state: ReplanState) -> dict[str, Any]:
    """返回结果节点.

    解析 LLM 返回的 JSON，提取行程数据。

    Args:
        state: 当前状态

    Returns:
        状态更新字典，包含 result 或 error
    """
    logger.info(f"[replan:return_result] 解析 LLM 响应 [plan:{state.plan_id}]")

    if state.error:
        logger.error(f"[replan:return_result] 上游已有错误: {state.error}")
        return {"result": None}

    if not state.llm_response:
        error_msg = "LLM 返回空响应"
        logger.error(f"[replan:return_result] {error_msg}")
        return {"error": error_msg, "result": None}

    try:
        # 清理 markdown 代码块标记
        content = state.llm_response.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        # 解析 JSON
        result = json.loads(content)
        logger.info(f"[replan:return_result] JSON 解析成功")

        return {"result": result, "error": None}

    except json.JSONDecodeError as e:
        error_msg = f"LLM 响应 JSON 解析失败: {e}"
        logger.error(f"[replan:return_result] {error_msg}")
        return {"error": error_msg, "result": None}


# =============================================================================
# StateGraph 构建
# =============================================================================


def build_replan_graph() -> StateGraph:
    """构建重新规划的 LangGraph StateGraph.

    图结构:
        collect_context --> call_llm --> return_result --> END

    Returns:
        编译好的 StateGraph 实例
    """
    # 创建图
    graph = StateGraph(ReplanState)

    # 添加节点
    graph.add_node("collect_context", collect_context)
    graph.add_node("call_llm", call_llm)
    graph.add_node("return_result", return_result)

    # 设置入口点
    graph.set_entry_point("collect_context")

    # 添加边
    graph.add_edge("collect_context", "call_llm")
    graph.add_edge("call_llm", "return_result")
    graph.add_edge("return_result", END)

    # 编译
    app = graph.compile()

    logger.info("[replan] LangGraph StateGraph 编译完成")
    return app


# 全局实例（延迟初始化）
_replan_graph: Optional[Any] = None


def get_replan_graph():
    """获取重新规划 StateGraph 实例（单例）.

    Returns:
        编译好的 StateGraph 实例
    """
    global _replan_graph
    if _replan_graph is None:
        _replan_graph = build_replan_graph()
    return _replan_graph
