from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Item
from app.crud import get_items, get_item, create_item, update_item, delete_item
from app.models import ItemORM

router = APIRouter()


# Dependency to get the database session
def get_db():
    """
    Provides a database session dependency for request handlers.

    Yields:
        Session: A SQLAlchemy database session object.

    Ensures the database session is closed after the request is completed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/items", response_model=list[Item], tags=["Supermarket"])
async def read_items(db: Session = Depends(get_db)):
    """
    Retrieve a list of all items from the inventory.

    Args:
        db (Session): Database session dependency.

    Returns:
        list[Item]: A list of `Item` objects representing items in the inventory.
    """
    return get_items(db)


@router.get("/items/{item_id}", response_model=Item, tags=["Supermarket"])
async def read_item(item_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single item by its ID.

    Args:
        item_id (int): The unique identifier of the item to retrieve.
        db (Session): Database session dependency.

    Returns:
        Item: An `Item` object representing the requested item, or `None` if not found.
    """
    return get_item(db, item_id)


@router.post("/items/", response_model=Item, tags=["Supermarket"])
async def add_item(item: Item, db: Session = Depends(get_db)):
    """
    Add a new item to the inventory.

    Args:
        item (Item): The `Item` object containing item details.
        db (Session): Database session dependency.

    Returns:
        Item: The newly created `Item` object.
    """
    item_orm = ItemORM(**item.model_dump())  # Convert to ORM instance
    return create_item(db, item_orm)


@router.put("/items/{item_id}", response_model=Item, tags=["Supermarket"])
async def modify_item(item_id: int, updated_item: Item, db: Session = Depends(get_db)):
    """
    Update an existing item in the inventory by its ID.

    Args:
        item_id (int): The unique identifier of the item to update.
        updated_item (Item): The `Item` object with updated details.
        db (Session): Database session dependency.

    Returns:
        Item: The updated `Item` object, or `None` if not found.
    """
    return update_item(db, item_id, updated_item.model_dump())


@router.delete("/items/{item_id}", tags=["Supermarket"])
async def remove_item(item_id: int, db: Session = Depends(get_db)):
    """
    Delete an item from the inventory by its ID.

    Args:
        item_id (int): The unique identifier of the item to delete.
        db (Session): Database session dependency.

    Returns:
        bool: `True` if the item was successfully deleted, otherwise `False`.
    """
    return delete_item(db, item_id)
