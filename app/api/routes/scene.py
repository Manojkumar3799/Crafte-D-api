from fastapi import APIRouter
from app.models.scene import SceneJSON, SceneObject, MaterialConfig, BehaviorConfig, GameConfig, TerrainConfig

router = APIRouter(prefix="/scene", tags=["scene"])

@router.get("/test", response_model=SceneJSON)
async def get_test_scene():
    """Returns a hardcoded test scene for Milestone 1 verification."""
    return SceneJSON(
        gameConfig=GameConfig(
            title="Pastel Floating Islands",
            description="Explore the floating islands and collect the glowing crystals!",
            cameraMode="third-person",
            winCondition={"type": "collect_all", "target": 3},
            playerStart=[0.0, 1.0, 0.0]
        ),
        terrain=TerrainConfig(
            enabled=True,
            size=30.0,
            segments=48,
            heightScale=2.5,
            seed=101,
            colorScheme="grassland"
        ),
        objects=[
            # Player character primitive
            SceneObject(
                id="player",
                name="Player Sphere",
                type="sphere",
                position=[0.0, 1.2, 0.0],
                scale=[0.8, 0.8, 0.8],
                material=MaterialConfig(color="#6366f1", roughness=0.3, metalness=0.2),
                behavior=BehaviorConfig(type="player")
            ),
            # Collectible 1
            SceneObject(
                id="gem_1",
                name="Crystal Gem 1",
                type="octahedron" if False else "torus",  # torus or box
                position=[-5.0, 1.5, -4.0],
                scale=[0.6, 0.6, 0.6],
                rotation=[0.5, 0.5, 0.0],
                material=MaterialConfig(color="#f59e0b", roughness=0.2, metalness=0.8, emissive="#fbbf24"),
                behavior=BehaviorConfig(type="collectible", points=10)
            ),
            # Collectible 2
            SceneObject(
                id="gem_2",
                name="Crystal Gem 2",
                type="torus",
                position=[6.0, 2.0, -2.0],
                scale=[0.6, 0.6, 0.6],
                rotation=[0.0, 0.8, 0.4],
                material=MaterialConfig(color="#ec4899", roughness=0.2, metalness=0.8, emissive="#f472b6"),
                behavior=BehaviorConfig(type="collectible", points=10)
            ),
            # Collectible 3
            SceneObject(
                id="gem_3",
                name="Crystal Gem 3",
                type="torus",
                position=[2.0, 1.5, 6.0],
                scale=[0.6, 0.6, 0.6],
                rotation=[0.4, 0.0, 0.6],
                material=MaterialConfig(color="#10b981", roughness=0.2, metalness=0.8, emissive="#34d399"),
                behavior=BehaviorConfig(type="collectible", points=10)
            ),
            # Tree / Pillar 1
            SceneObject(
                id="pillar_1",
                name="Ancient Pillar",
                type="cylinder",
                position=[-6.0, 2.0, 5.0],
                scale=[0.8, 4.0, 0.8],
                material=MaterialConfig(color="#cbd5e1", roughness=0.6, metalness=0.1),
                behavior=BehaviorConfig(type="static")
            ),
            # Decorative Box
            SceneObject(
                id="box_1",
                name="Wooden Crate",
                type="box",
                position=[4.0, 0.8, 4.0],
                scale=[1.2, 1.2, 1.2],
                material=MaterialConfig(color="#d97706", roughness=0.8),
                behavior=BehaviorConfig(type="static")
            )
        ],
        environment={
            "skyColor": "#f0f9ff",
            "groundColor": "#dcfce7",
            "ambientLight": 0.8,
            "directionalLight": 1.2
        }
    )
