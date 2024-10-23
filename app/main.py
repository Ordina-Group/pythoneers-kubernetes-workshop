import os
import signal
import asyncio
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.requests import Request


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

# Create (POST)
@app.post("/items/", response_model=Item,  description="Add a new item to the list.",)
async def create_item(item: Item):
    items.append(item)
    return item

# Read (GET all)
@app.get("/items", response_model=List[Item], description="Overview of all items.")
async def read_items():
    return items

# Read (GET single item)
@app.get("/items/{item_id}", response_model=Item, description="Get a specific item based on ID.")
async def read_item(item_id: int):
    for item in items:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

# Update (PUT)
@app.put("/items/{item_id}", response_model=Item, description="Update an existing item based on ID.")
async def update_item(item_id: int, updated_item: Item):
    for index, item in enumerate(items):
        if item.id == item_id:
            items[index] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found")

# Delete (DELETE)
@app.delete("/items/{item_id}", description="Delete an existing item based on ID.")
async def delete_item(item_id: int):
    for index, item in enumerate(items):
        if item.id == item_id:
            del items[index]
            return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")

# Read (GET all)
@app.get("/crash", description="Crash the entire service in 5 seconds.", tags=["test"] )
async def crash_app():
    # Countdown from 5 seconds before crashing
    for i in range(5, 0, -1):
        print(f"Application will crash in {i} seconds...")
        await asyncio.sleep(1)  # Wait for 1 second

    # Log the final crash message
    print("The application is about to crash!")

    os.kill(os.getpid(), signal.SIGTERM)
    return Response(status_code=200, content='Server shutting down...')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='localhost', port=8000, loop="asyncio")