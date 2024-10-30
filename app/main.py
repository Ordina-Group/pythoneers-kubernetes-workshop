import os
import signal
import asyncio
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.requests import Request

from sqlalchemy import create_engine, Column, Integer, String, Float, exc
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "mysql://app_user:app_password@localhost:3306/app_db")

# Attempt to create the SQLAlchemy engine and session
try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    # Define User model
    class ItemORM(Base):
        __tablename__= "inventory"
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
    version="1.0.0"
)

# Mount the static folder to serve CSS and other static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates using Jinja2
templates = Jinja2Templates(directory="templates")


# Define a data model
class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    quantity: int


# In-memory "database"
items = []


# Root endpoint
@app.get("/",  include_in_schema=False, response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Serve the favicon
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("../ico/python.ico")


# Read (GET all)
@app.get("/items", response_model=list[Item], description="Overview of all items.",  tags=["Supermarket"])
async def read_items():
    if db_available:
        # If the database is available, query from the database
        print("You're using the database connection")
        with SessionLocal() as db:
            db_items = db.query(ItemORM).all()
            return db_items
    else:
        # If the database is not available, return the in-memory list
        print("You're using the local list")
        return items


# Read (GET single item)
@app.get("/items/{item_id}", response_model=Item, description="Get a specific item based on ID.", tags=["Supermarket"])
async def read_item(item_id: int):
    if db_available:
        print("You're using the database connection")
        with SessionLocal() as db:
            item = db.query(ItemORM).filter(ItemORM.id == item_id).first()
            if item:
                return item
    else:
        print("You're using the local list")
        for item in items:
            if item.id == item_id:
                return item
    raise HTTPException(status_code=404, detail="Item not found")


# Create (POST)
@app.post("/items/", response_model=Item,  description="Add a new item to the list.", tags=["Supermarket"])
async def create_item(item: Item):
    if db_available:
        print("You're using the database connection")
        with SessionLocal() as db:
            db_item = ItemORM(**item.dict())
            db.add(db_item)
            db.commit()
            db.refresh(db_item)
            return db_item
    else:
        print("You're using the local list")
        items.append(item)
        return item


# Update (PUT)
@app.put("/items/{item_id}", response_model=Item, description="Update an existing item based on ID.", tags=["Supermarket"])
async def update_item(item_id: int, updated_item: Item):
    if db_available:
        print("You're using the database connection")
        with SessionLocal() as db:
            db_item = db.query(ItemORM).filter(ItemORM.id == item_id).first()
            if db_item:
                for key, value in updated_item.dict().items():
                    setattr(db_item, key, value)
                db.commit()
                return db_item
    else:
        print("You're using the local list")
        for index, item in enumerate(items):
            if item.id == item_id:
                items[index] = updated_item
                return updated_item
    raise HTTPException(status_code=404, detail="Item not found")


# Delete (DELETE)
@app.delete("/items/{item_id}", description="Delete an existing item based on ID.", tags=["Supermarket"])
async def delete_item(item_id: int):
    if db_available:
        print("You're using the database connection")
        with SessionLocal() as db:
            item = db.query(ItemORM).filter(ItemORM.id == item_id).first()
            if item:
                db.delete(item)
                db.commit()
                return {"message": "Item deleted successfully"}
    else:
        print("You're using the local list")
        for index, item in enumerate(items):
            if item.id == item_id:
                del items[index]
                return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")


# Read (GET all)
@app.get("/crash", description="Crash the entire service in 5 seconds.", tags=["crash"] )
async def crash_app():
    # Countdown from 5 seconds before crashing
    for i in range(5, 0, -1):
        print(f"Application will crash in {i} seconds...")
        await asyncio.sleep(1)  # Wait for 1 second

    # Log the final crash message
    print("The application is about to crash!")

    os.kill(os.getpid(), signal.SIGTERM)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='localhost', port=8000, loop="asyncio")