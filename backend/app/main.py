from fastapi import FastAPI

from app.routers import auth

app = FastAPI(
    title="futbol-app API",
    description="API para organizar partidos de fútbol amateur",
    version="0.1.0",
)

app.include_router(auth.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
