from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
import sys

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "src" / "static"

# Keep imports stable even if the process is started from another working directory.
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.rss_manager import RSSManager
from src.api.routes import router, set_rss_manager
from src.api.constants import router as constants_router
from src.general.general_constant import APP_VERSION, get_app_version

app = FastAPI(version=APP_VERSION)
rss = RSSManager()
# Set the RSSManager instance for API routes
set_rss_manager(rss)

# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["api"])
app.include_router(constants_router, prefix="/api", tags=["constants"])

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.on_event("startup")
def startup_event():
    rss.start_all()

# -------------------------------
# Root endpoint
# -------------------------------
@app.get("/")
def root():
    # Serve HTML file if it exists, otherwise return API info
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path), media_type="text/html")
    return {
        "message": "RSS to Transmission Manager API",
        "version": get_app_version(),
        "docs": "/docs",
        "endpoints": {
            "rss": "/api/rss",
            "feeds": "/api/feeds",
            "settings": "/api/settings"
        }
    }
