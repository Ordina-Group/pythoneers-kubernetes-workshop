from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from app.routers import item_router, admin_router

# Initialize FastAPI app
app = FastAPI(
    title="Supermarket Application",
    description="This is a supermarket application for the Kubernetes workshop.",
    version="1.0.0",
)

# Mount the static folder to serve CSS and other static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up templates using Jinja2
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(item_router.router)
app.include_router(admin_router.router)


@app.get("/", include_in_schema=False, response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Root endpoint that renders the index.html template.

    Args:
        request (Request): The current request.

    Returns:
        HTMLResponse: The rendered HTML response for the index page.
    """
    return templates.TemplateResponse("index.html", {"request": request})


# Serve the favicon
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/ico/python.ico")
