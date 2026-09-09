from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

class MaterialConfig(BaseModel):
    color: str = "#888888"
    roughness: float = 0.5
    metalness: float = 0.1
    emissive: Optional[str] = None
    wireframe: bool = False

class BehaviorConfig(BaseModel):
    type: Literal["static", "player", "collectible", "obstacle", "enemy", "goal", "moving"] = "static"
    points: int = 0
    damage: int = 0
    speed: float = 0.0
    axis: Optional[Literal["x", "y", "z"]] = "y"
    range: float = 0.0

class SceneObject(BaseModel):
    id: str
    name: str
    type: Literal["box", "sphere", "cylinder", "cone", "torus", "plane", "asset"] = "box"
    position: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    scale: List[float] = Field(default_factory=lambda: [1.0, 1.0, 1.0])
    material: MaterialConfig = Field(default_factory=MaterialConfig)
    behavior: Optional[BehaviorConfig] = None
    assetId: Optional[str] = None
    assetUrl: Optional[str] = None

class TerrainConfig(BaseModel):
    enabled: bool = True
    size: float = 40.0
    segments: int = 64
    heightScale: float = 3.0
    seed: int = 42
    colorScheme: Literal["grassland", "desert", "arctic", "sci-fi"] = "grassland"

class GameConfig(BaseModel):
    title: str = "Mini Game"
    description: str = "A generated 3D mini-game"
    cameraMode: Literal["third-person", "first-person", "top-down"] = "third-person"
    winCondition: Dict[str, Any] = Field(default_factory=lambda: {"type": "collect_all", "target": 3})
    loseCondition: Dict[str, Any] = Field(default_factory=lambda: {"type": "none"})
    playerStart: List[float] = Field(default_factory=lambda: [0.0, 1.0, 0.0])

class SceneJSON(BaseModel):
    gameConfig: GameConfig = Field(default_factory=GameConfig)
    terrain: Optional[TerrainConfig] = Field(default_factory=TerrainConfig)
    objects: List[SceneObject] = Field(default_factory=list)
    environment: Dict[str, Any] = Field(default_factory=lambda: {
        "skyColor": "#e0f2fe",
        "groundColor": "#86efac",
        "ambientLight": 0.7,
        "directionalLight": 1.2
    })
