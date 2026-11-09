from fastapi import FastAPI

app = FastAPI(
    title="futbol-app API",
    description="API para organizar partidos de fútbol amateur",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}
