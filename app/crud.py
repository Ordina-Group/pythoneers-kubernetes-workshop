from sqlalchemy.orm import Session
from app.models import ItemORM
from app.database import db_available

# In-memory "database"
items = []


def get_items(db: Session):
    """
    Retrieve all items from the database or local in-memory list if the database is unavailable.

    Args:
        db (Session): SQLAlchemy database session.

    Returns:
        list: A list of `ItemORM` instances from the database, or from the local `items` list if `db_available` is False.
    """
    if db_available:
        return db.query(ItemORM).all()
    else:
        return items  # Return the local list if the database is unavailable


def get_item(db: Session, item_id: int):
    """
    Retrieve a single item by ID from the database or from the in-memory list if the database is unavailable.

    Args:
        db (Session): SQLAlchemy database session.
        item_id (int): The unique identifier of the item to retrieve.

    Returns:
        ItemORM or None: The item with the specified ID if found, otherwise None.
    """
    if db_available:
        return db.query(ItemORM).filter(ItemORM.id == item_id).first()
    else:
        for item in items:
            if item.id == item_id:
                return item
    return None


def create_item(db: Session, item: ItemORM):
    """
    Add a new item to the database or to the in-memory list if the database is unavailable.

    Args:
        db (Session): SQLAlchemy database session.
        item (ItemORM): The item instance to be added.

    Returns:
        ItemORM: The newly added item instance.
    """
    if db_available:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    else:
        items.append(item)  # Append the new item to the local list
        return item


def update_item(db: Session, item_id: int, item_data: dict):
    """
    Update an existing item with new data in the database or in the in-memory list if the database is unavailable.

    Args:
        db (Session): SQLAlchemy database session.
        item_id (int): The unique identifier of the item to update.
        item_data (dict): A dictionary containing the updated item attributes.

    Returns:
        ItemORM or None: The updated item instance if successful, otherwise None.
    """
    if db_available:
        item = get_item(db, item_id)
        if item:
            for key, value in item_data.items():
                setattr(item, key, value)
            db.commit()
            return item
    else:
        for index, item in enumerate(items):
            if item.id == item_id:
                for key, value in item_data.items():
                    setattr(items[index], key, value)
                return items[index]
    return None


def delete_item(db: Session, item_id: int):
    """
    Delete an item by ID from the database or from the in-memory list if the database is unavailable.

    Args:
        db (Session): SQLAlchemy database session.
        item_id (int): The unique identifier of the item to delete.

    Returns:
        bool: True if the item was successfully deleted, otherwise False.
    """
    if db_available:
        item = get_item(db, item_id)
        if item:
            db.delete(item)
            db.commit()
            return True
    else:
        for index, item in enumerate(items):
            if item.id == item_id:
                del items[index]
                return True
    return False
