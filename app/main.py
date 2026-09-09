from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import scene

app = FastAPI(
    title="Crafter D API",
    description="AI-powered 3D Mini-Game Generator Backend",
    version="1.0.0"
)

# CORS middleware for local frontend & Cloudflare Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows local Vite server and deployed frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scene.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Crafter D Engine API is active", "status": "online"}
