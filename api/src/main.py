from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config
from .routes import landscape

app = FastAPI(title="Emotion-Aware Analytics System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(landscape.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
