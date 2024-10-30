import fastapi
from app.schemas import item

# Read (GET all)
# In-memory "database"
items = []

router = fastapi.APIRouter(prefix="/supermarkt", tags=["Supermarket"])


@router.get(
    "/items", response_model=list[item.Item], description="Overview of all items."
)
async def read_items():
    if db_available:
        # If the database is available, query from the database
        print("You're using the database connection")
        with SessionLocal() as db:
            db_items = db.query(User).all()
            return db_items
    else:
        # If the database is not available, return the in-memory list
        print("You're using the local list")
        return items


# Read (GET single item)
@router.get(
    "/items/{item_id}",
    response_model=item.Item,
    description="Get a specific item based on ID.",
)
async def read_item(item_id: int):
    if db_available:
        print("You're using the database connection")
        with SessionLocal() as db:
            item = db.query(User).filter(User.id == item_id).first()
            if item:
                return item
    else:
        print("You're using the local list")
        for item in items:
            if item.id == item_id:
                return item
    raise fastapi.HTTPException(status_code=404, detail="item.Item not found")


# Create (POST)
@router.post(
    "/items/", response_model=item.Item, description="Add a new item to the list."
)
async def create_item(item: item.Item):
    if db_available:
        print("You're using the database connection")
        with SessionLocal() as db:
            db.add(User(**item.dict()))
            db.commit()
            db.refresh(item)
            return item
    else:
        print("You're using the local list")
        items.append(item)
        return item


# Update (PUT)
@router.put(
    "/items/{item_id}",
    response_model=item.Item,
    description="Update an existing item based on ID.",
)
async def update_item(item_id: int, updated_item: item.Item):
    if db_available:
        print("You're using the database connection")
        with SessionLocal() as db:
            db_item = db.query(User).filter(User.id == item_id).first()
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
    raise fastapi.HTTPException(status_code=404, detail="item.Item not found")


# Delete (DELETE)
@router.delete(
    "/items/{item_id}",
    description="Delete an existing item based on ID.",
)
async def delete_item(item_id: int):
    if db_available:
        print("You're using the database connection")
        with SessionLocal() as db:
            item = db.query(User).filter(User.id == item_id).first()
            if item:
                db.delete(item)
                db.commit()
                return {"message": "item.Item deleted successfully"}
    else:
        print("You're using the local list")
        for index, item in enumerate(items):
            if item.id == item_id:
                del items[index]
                return {"message": "item.Item deleted successfully"}
    raise fastapi.HTTPException(status_code=404, detail="item.Item not found")
