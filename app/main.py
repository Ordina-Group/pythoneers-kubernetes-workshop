import fastapi
from fastapi import staticfiles, templating

from app.routers import item_router, admin_router

# Initialize FastAPI app
app = fastapi.FastAPI(
    title="Supermarket Application",
    description="This is a supermarket application for the Kubernetes workshop.",
    version="1.0.0",
)

# Mount the static folder to serve CSS and other static files
app.mount("/static", staticfiles.StaticFiles(directory="app/static"), name="static")

# Set up templates using Jinja2
templates = templating.Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(item_router.router)
app.include_router(admin_router.router)

@app.middleware("http")
async def catch_exceptions(request: fastapi.Request, call_next):
    """
    Middleware that catches exceptions and returns a 500 response.

    Args:
        request (Request): The current request.
        call_next: The next middleware in the chain.

    Returns:
        Response: The response from the next middleware or the exception response.
    """
    try:
        return await call_next(request)
    except Exception as e:
        return fastapi.responses.JSONResponse(
            status_code=500, content={"message": str(e)}
        )

@app.get("/", include_in_schema=False, response_class=fastapi.responses.HTMLResponse)
async def read_root(request: fastapi.requests.Request):
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
    return fastapi.responses.FileResponse("app/ico/python.ico")
