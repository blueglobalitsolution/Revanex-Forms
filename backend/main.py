import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from backend.config import APP_NAME, APP_URL
from backend.database import init_db
from backend.routes.forms import router as forms_router
from backend.routes.submissions import router as submissions_router
from backend.routes.payments import router as payments_router
from backend.routes.auth import router as auth_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title=APP_NAME, version="1.0.0")

origins = ["http://localhost:8000", "http://127.0.0.1:8000", "http://localhost:5173", "http://127.0.0.1:5173"]
if APP_URL and "localhost" not in APP_URL and "127.0.0.1" not in APP_URL:
    origins.append(APP_URL)

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["127.0.0.1", "::1"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(forms_router)
app.include_router(submissions_router)
app.include_router(payments_router)

import os
from fastapi.responses import FileResponse

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/dashboard")
async def get_dashboard():
    return FileResponse("static/dashboard.html")

@app.get("/login")
async def get_login():
    return FileResponse("static/login.html")

@app.get("/create-form")
async def get_create_form():
    return FileResponse("static/create-form.html")

@app.get("/submissions")
async def get_submissions():
    return FileResponse("static/submissions.html")

@app.get("/settings")
async def get_settings():
    return FileResponse("static/settings.html")

@app.get("/form")
async def get_form():
    return FileResponse("static/form.html")

app.mount("/", StaticFiles(directory="static", html=True), name="static")


@app.on_event("startup")
def on_startup():
    try:
        init_db()
        logger.info("Database tables created / verified")
    except Exception as e:
        logger.error("Database initialization failed: %s", str(e))
        logger.warning("Server will start, but DB operations may fail until the database is available")
