"""Execute plan node using adapter pattern."""
from typing import Dict, Any
import asyncio
from app.domain.apps.base import ConnectedAppConfig, PlanStep, StepResult
from app.domain.apps.registry import get_adapter
from app.core.logging import get_logger

logger = get_logger(__name__)


async def execute_plan_step(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a single plan step using adapter pattern.
    Generic for all apps - uses adapter to dispatch.
    
    Args:
        state: Current graph state with plan and connected_app
        
    Returns:
        Updated state with step result
    """
    plan = state.get("plan", {})
    steps = plan.get("steps", [])
    current_step_index = state.get("current_step_index", 0)
    connected_app = state.get("connected_app")
    
    if not connected_app:
        state["error"] = "No app connection available"
        return state
    
    if current_step_index >= len(steps):
        # All steps completed
        state["answer"] = "Tất cả các bước đã được thực thi thành công."
        return state
    
    # Execute current step
    step_dict = steps[current_step_index]
    step = PlanStep(
        id=step_dict.get("id", current_step_index + 1),
        action=step_dict.get("action", ""),
        params=step_dict.get("params", {})
    )
    
    logger.info(f"Executing step {current_step_index + 1}/{len(steps)}: {step.action}")
    
    try:
        # Build ConnectedAppConfig from state
        app_config = ConnectedAppConfig(**connected_app.get("config", {}))
        
        # Get adapter and execute step
        adapter = get_adapter(app_config.app_id)
        result = adapter.execute_step(step, app_config)
        
        # Record step result
        step_result_dict = {
            "step_id": result.step_id,
            "action": step.action,
            "status": result.status,
            "output": result.raw,
            "error": result.message if result.status == "failed" else None,
        }
        
        if "step_results" not in state:
            state["step_results"] = []
        state["step_results"].append(step_result_dict)
        state["current_step_index"] = current_step_index + 1
        
        logger.info(f"Step {current_step_index + 1} completed: {result.status}")
        
    except Exception as e:
        error = str(e)
        logger.error(f"Step execution error: {error}", exc_info=True)
        step_result_dict = {
            "step_id": step.id,
            "action": step.action,
            "status": "failed",
            "output": None,
            "error": error
        }
        if "step_results" not in state:
            state["step_results"] = []
        state["step_results"].append(step_result_dict)
        state["current_step_index"] = current_step_index + 1
    
    return state


def execute_plan_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronous wrapper for execute_plan_step.
    For use in LangGraph nodes that require synchronous functions.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, use thread pool
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, execute_plan_step(state))
                return future.result()
        else:
            return asyncio.run(execute_plan_step(state))
    except RuntimeError:
        # No event loop, create new one
        return asyncio.run(execute_plan_step(state))
