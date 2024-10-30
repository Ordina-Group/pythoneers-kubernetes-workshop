import os
import signal
import asyncio

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from sqlalchemy import create_engine, Column, Integer, String, Float, exc
from sqlalchemy.orm import sessionmaker, declarative_base

from app.api import supermarkt

DATABASE_URL = os.getenv(
    "DATABASE_URL", "mysql://app_user:app_password@localhost:3306/app_db"
)

# Attempt to create the SQLAlchemy engine and session
try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    # Define User model
    class User(Base):
        __tablename__ = "inventory"
        id = Column(Integer, primary_key=True, index=True)
        name = Column(String(length=20), index=True)
        description = Column(String(length=100), index=True)
        price = Column(Float, index=True)
        quantity = Column(Integer, index=True)

        # Try to create tables if the connection is available

    Base.metadata.create_all(bind=engine)

    # If the connection is successful, set this flag to True
    db_available = True

except exc.SQLAlchemyError as e:
    print(f"Database connection failed: {e}")
    db_available = False


app = FastAPI(
    title="Supermarket Application",
    description="This is a supermarket application for the kubernetes workshop.",
    version="1.0.0",
)

# Mount the static folder to serve CSS and other static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates using Jinja2
templates = Jinja2Templates(directory="templates")


# Root endpoint
@app.get("/", include_in_schema=False, response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Serve the favicon
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("../ico/python.ico")

# Read (GET all)
@app.get("/crash", description="Crash the entire service in 5 seconds.", tags=["crash"])
async def crash_app():
    # Countdown from 5 seconds before crashing
    for i in range(5, 0, -1):
        print(f"Application will crash in {i} seconds...")
        await asyncio.sleep(1)  # Wait for 1 second

    # Log the final crash message
    print("The application is about to crash!")

    os.kill(os.getpid(), signal.SIGTERM)


app.include_router(supermarkt.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000, loop="asyncio")
