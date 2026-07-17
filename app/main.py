from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.api import scrape_routes, email_routes, schedule_routes

app = FastAPI(title="Lead Automation System")

app.include_router(scrape_routes.router)
app.include_router(email_routes.router)
app.include_router(schedule_routes.router)


@app.get("/api-status")
def health_check():
    return {"status": "ok", "environment": settings.environment}


@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")


app.mount("/static", StaticFiles(directory="static"), name="static")