import logging
from typing import Dict, Any, TypedDict, Optional
from langgraph.graph import StateGraph, END
from app.services.llm import generate_scene_from_llm
from app.models.scene import SceneJSON

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    prompt: str
    scene_dict: Optional[Dict[str, Any]]
    error: Optional[str]
    retry_count: int
    is_valid: bool

async def planner_node(state: AgentState) -> AgentState:
    """Invokes LLM provider (Groq/Gemini/Fallback) to construct scene JSON structure."""
    prompt = state["prompt"]
    retry_count = state.get("retry_count", 0)
    logger.info(f"LangGraph Agent Executing Planner Node (attempt {retry_count + 1}) for prompt: '{prompt}'")

    try:
        raw_scene = await generate_scene_from_llm(prompt)
        return {
            "prompt": prompt,
            "scene_dict": raw_scene,
            "error": None,
            "retry_count": retry_count,
            "is_valid": False
        }
    except Exception as err:
        logger.error(f"Planner node exception: {err}")
        return {
            "prompt": prompt,
            "scene_dict": None,
            "error": str(err),
            "retry_count": retry_count + 1,
            "is_valid": False
        }

def validator_node(state: AgentState) -> AgentState:
    """Validates generated raw dictionary against Pydantic SceneJSON schema."""
    raw_dict = state.get("scene_dict")
    retry_count = state.get("retry_count", 0)

    if not raw_dict:
        return {**state, "is_valid": False, "error": "Empty scene payload"}

    try:
        # Validate Pydantic schema
        validated_scene = SceneJSON(**raw_dict)
        logger.info(f"Validator Node: Scene validated successfully with {len(validated_scene.objects)} objects.")
        return {
            **state,
            "scene_dict": validated_scene.model_dump(),
            "is_valid": True,
            "error": None
        }
    except Exception as val_err:
        logger.warning(f"Validator Node Validation Failure: {val_err}")
        return {
            **state,
            "is_valid": False,
            "error": str(val_err),
            "retry_count": retry_count + 1
        }

def should_continue(state: AgentState) -> str:
    """Determines whether to finish execution or retry planning on error."""
    if state.get("is_valid", False):
        return "end"
    if state.get("retry_count", 0) >= 2:
        logger.warning("Max retries reached in LangGraph agent loop. Stopping.")
        return "end"
    return "retry"

def build_game_agent_graph():
    """Constructs and compiles the LangGraph state machine."""
    workflow = StateGraph(AgentState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("validator", validator_node)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "validator")

    workflow.add_conditional_edges(
        "validator",
        should_continue,
        {
            "end": END,
            "retry": "planner"
        }
    )

    return workflow.compile()

# Single instance compiled graph
game_agent_graph = build_game_agent_graph()
