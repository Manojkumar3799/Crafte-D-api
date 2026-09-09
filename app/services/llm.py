import os
import json
import logging
from typing import Dict, Any, Optional
from app.models.scene import SceneJSON
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Try loading LangChain wrappers
try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

SYSTEM_PROMPT = """You are an expert 3D Mini-Game Designer and Level Architect for Crafter D.
Your job is to convert natural-language user prompts into a structured, playable 3D mini-game level represented strictly as JSON.

Follow these strict design principles:
1. SCOPE: Keep mini-games self-contained, fun, and easy to complete (1-5 minutes playtime).
2. GEOMETRY TYPES: Use ONLY primitive geometry types: "box", "sphere", "cylinder", "cone", "torus", "plane".
3. PALETTE & THEME: Select pastel, harmonious, elegant color schemes (e.g., grassland, desert, arctic, sci-fi).
4. LAYOUT & HEIGHT:
   - Always place objects above or on the terrain surface (y >= 0.5 for small items, y >= 1.0 for larger objects).
   - Provide 3-8 collectibles (torus or sphere with emissive colors).
   - Provide 1 player object (sphere or box marked with behavior type "player").
   - Provide 2-6 static/moving obstacles or platforms.
5. GAME CONFIG:
   - Provide a creative title and brief description.
   - Select camera mode: "third-person" (platformer/adventure), "top-down" (maze/puzzle), or "first-person".
   - Define win condition: {"type": "collect_all", "target": number_of_collectibles} or {"type": "reach_goal"}.

You MUST reply with ONLY valid JSON matching the SceneJSON schema. Do not add markdown code fences, quotes around the JSON block, or extra text."""

def get_fallback_mock_scene(user_prompt: str) -> Dict[str, Any]:
    """Generates a procedural dynamic scene if no LLM API keys are provided yet."""
    import random
    seed = random.randint(100, 999)
    is_desert = "desert" in user_prompt.lower() or "dune" in user_prompt.lower()
    is_scifi = "sci-fi" in user_prompt.lower() or "alien" in user_prompt.lower() or "space" in user_prompt.lower()
    
    color_scheme = "desert" if is_desert else ("sci-fi" if is_scifi else "grassland")
    sky = "#ffedd5" if is_desert else ("#fae8ff" if is_scifi else "#e0f2fe")
    
    return {
        "gameConfig": {
            "title": f"Agent Crafted: {user_prompt[:25]}...",
            "description": f"Generated game for prompt: '{user_prompt}'",
            "cameraMode": "top-down" if "maze" in user_prompt.lower() else "third-person",
            "winCondition": {"type": "collect_all", "target": 4},
            "playerStart": [0.0, 1.2, 0.0]
        },
        "terrain": {
            "enabled": True,
            "size": 36.0,
            "segments": 48,
            "heightScale": 3.0,
            "seed": seed,
            "colorScheme": color_scheme
        },
        "objects": [
            {
                "id": "player_1",
                "name": "Hero Ball",
                "type": "sphere",
                "position": [0.0, 1.2, 0.0],
                "scale": [0.8, 0.8, 0.8],
                "material": {"color": "#4f46e5", "roughness": 0.2, "metalness": 0.3},
                "behavior": {"type": "player"}
            },
            {
                "id": "c1",
                "name": "Amber Star",
                "type": "torus",
                "position": [-5.0, 1.5, -4.0],
                "scale": [0.5, 0.5, 0.5],
                "material": {"color": "#f59e0b", "emissive": "#fbbf24", "metalness": 0.8},
                "behavior": {"type": "collectible", "points": 10}
            },
            {
                "id": "c2",
                "name": "Ruby Star",
                "type": "torus",
                "position": [6.0, 1.8, -2.0],
                "scale": [0.5, 0.5, 0.5],
                "material": {"color": "#e11d48", "emissive": "#f43f5e", "metalness": 0.8},
                "behavior": {"type": "collectible", "points": 10}
            },
            {
                "id": "c3",
                "name": "Sapphire Star",
                "type": "torus",
                "position": [2.0, 1.5, 6.0],
                "scale": [0.5, 0.5, 0.5],
                "material": {"color": "#0284c7", "emissive": "#38bdf8", "metalness": 0.8},
                "behavior": {"type": "collectible", "points": 10}
            },
            {
                "id": "c4",
                "name": "Emerald Star",
                "type": "torus",
                "position": [-4.0, 1.5, 5.0],
                "scale": [0.5, 0.5, 0.5],
                "material": {"color": "#059669", "emissive": "#34d399", "metalness": 0.8},
                "behavior": {"type": "collectible", "points": 10}
            },
            {
                "id": "p1",
                "name": "Floating Platform",
                "type": "box",
                "position": [0.0, 0.5, -5.0],
                "scale": [3.0, 0.5, 3.0],
                "material": {"color": "#a855f7", "roughness": 0.4},
                "behavior": {"type": "moving", "axis": "x", "range": 3.0, "speed": 1.2}
            },
            {
                "id": "ob1",
                "name": "Ancient Spire",
                "type": "cone",
                "position": [-6.0, 2.0, -1.0],
                "scale": [1.0, 4.0, 1.0],
                "material": {"color": "#78716c", "roughness": 0.7},
                "behavior": {"type": "static"}
            }
        ],
        "environment": {
            "skyColor": sky,
            "groundColor": "#dcfce7",
            "ambientLight": 0.8,
            "directionalLight": 1.2
        }
    }

async def generate_scene_from_llm(prompt: str) -> Dict[str, Any]:
    """
    Primary Provider: Groq API (llama-3.3-70b-versatile)
    Fallback Provider: Gemini API (gemini-2.5-flash / gemini-1.5-flash)
    Fallback 2: Procedural game engine generator if keys are unpopulated placeholders.
    """
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()

    has_groq = bool(groq_key and "your_" not in groq_key)
    has_gemini = bool(gemini_key and "your_" not in gemini_key)

    # 1. Try Groq API
    if has_groq and ChatGroq is not None:
        try:
            logger.info("Calling primary LLM provider: Groq API")
            llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                groq_api_key=groq_key,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            response = await llm.ainvoke([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Create a 3D mini-game scene for this prompt: '{prompt}'"}
            ])
            text = response.content.strip()
            data = json.loads(text)
            logger.info("Successfully received Groq response")
            return data
        except Exception as e:
            logger.warning(f"Groq API call failed: {e}. Falling back to Gemini...")

    # 2. Try Gemini API as fallback
    if has_gemini and ChatGoogleGenerativeAI is not None:
        try:
            logger.info("Calling fallback LLM provider: Gemini API")
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=gemini_key,
                temperature=0.7
            )
            response = await llm.ainvoke([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Create a 3D mini-game scene for this prompt: '{prompt}'"}
            ])
            text = response.content.strip()
            # Clean markdown code blocks if any
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            data = json.loads(text.strip())
            logger.info("Successfully received Gemini response")
            return data
        except Exception as e:
            logger.warning(f"Gemini API call failed: {e}. Falling back to dynamic procedural mock generator...")

    # 3. Dynamic procedural fallback generator
    logger.info("No valid active LLM API keys detected. Generating procedural scene...")
    return get_fallback_mock_scene(prompt)
