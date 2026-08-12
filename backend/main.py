import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.eureka.routes import router as eureka_router

# Resolve absolute paths relative to backend directory
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(BACKEND_DIR)  # d:\Entreprenuership club\Eureka
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

# Ensure required directories exist at launch to prevent StaticFiles errors
os.makedirs(os.path.join(FRONTEND_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(FRONTEND_DIR, "js"), exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# 1. Initialize database tables
Base.metadata.create_all(bind=engine)

# 2. Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Decoupled Modular Registration Backend for Event Sites",
    version="1.0.0"
)

# 3. Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Register modular routers
app.include_router(eureka_router, prefix="/api/eureka", tags=["Eureka Pitching"])

# 5. Serve frontend HTML views
def serve_frontend_page(filename: str):
    page_path = os.path.join(FRONTEND_DIR, filename)
    if os.path.exists(page_path):
        return FileResponse(page_path)
    return {"message": f"{filename} not created yet."}


@app.get("/")
def read_index():
    return serve_frontend_page("index.html")


@app.get("/index.html")
def read_index_html():
    return serve_frontend_page("index.html")

@app.get("/register")
def read_register():
    return serve_frontend_page("register.html")


@app.get("/register.html")
def read_register_html():
    return serve_frontend_page("register.html")

@app.get("/admin")
def read_admin():
    return serve_frontend_page("admin.html")


@app.get("/admin.html")
def read_admin_html():
    return serve_frontend_page("admin.html")

# 6. Mount CSS, JS and Upload static assets
app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
