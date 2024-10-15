from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Define a data model
class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    quantity: int

# In-memory "database"
items = []

# Create (POST)
@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    items.append(item)
    return item

# Read (GET all)
@app.get("/items/", response_model=List[Item])
async def read_items():
    return items

# Read (GET single item)
@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    for item in items:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

# Update (PUT)
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, updated_item: Item):
    for index, item in enumerate(items):
        if item.id == item_id:
            items[index] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found")

# Delete (DELETE)
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    for index, item in enumerate(items):
        if item.id == item_id:
            del items[index]
            return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")
