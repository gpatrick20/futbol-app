from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    auth,
    availability,
    match_events,
    matches,
    payments,
    results,
    teams,
)

app = FastAPI(
    title="futbol-app API",
    description="API para organizar partidos de fútbol amateur",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(teams.router)
app.include_router(matches.router)
app.include_router(availability.router)
app.include_router(payments.router)
app.include_router(match_events.router)
app.include_router(results.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
