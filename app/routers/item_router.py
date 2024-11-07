import fastapi
from app import database, models

router = fastapi.APIRouter(tags=["Supermarket Inventory"])


class DBNotAvailableError(fastapi.HTTPException):
    def __init__(self):
        super().__init__(
            status_code=fastapi.status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not available",
        )


@router.get("/items")
async def read_items(
    db_repo: database.DatabaseRepository = fastapi.Depends(database.DatabaseRepository)
) -> list[models.Item]:
    """Retrieve a list of all items from the inventory.

    Args:
        db_repo: Database repository dependency.

    Raises:
        DBNotAvailableError: If the database is not available.


    Returns:
        list[Item]: A list of `Item` objects representing items in the inventory.
    """
    if not db_repo.connected():
        raise DBNotAvailableError
    return db_repo.get_items()


@router.get("/items/{item_id}")
async def read_item(
    item_id: int,
    db_repo: database.DatabaseRepository = fastapi.Depends(database.DatabaseRepository),
) -> models.Item:
    """Retrieve a single item by its ID.

    Args:
        item_id (int): The unique identifier of the item to retrieve.
        db_repo: Database repository dependency.

    Raises:
        DBNotAvailableError: If the database is not available.

    Returns:
        Item: An `Item` object representing the requested item, or `None` if not found.
    """

    if not db_repo.connected():
        raise DBNotAvailableError
    return db_repo.get_item(item_id)


@router.post("/items/")
async def add_item(
    item: models.Item,
    db_repo: database.DatabaseRepository = fastapi.Depends(database.DatabaseRepository),
) -> models.Item:
    """Add a new item to the inventory.

    Args:
        item (Item): The `Item` object containing item details.
        db_repo: Database repository dependency.

    Raises:
        DBNotAvailableError: If the database is not available.


    Returns:
        Item: The newly created `Item` object.
    """
    if not db_repo.connected():
        raise DBNotAvailableError

    return db_repo.create_item(item)


@router.put("/items/{item_id}")
async def modify_item(
    item_id: int,
    updated_item: models.Item,
    db_repo: database.DatabaseRepository = fastapi.Depends(database.DatabaseRepository),
) -> models.Item:
    """Update an existing item in the inventory by its ID.

    Args:
        item_id (int): The unique identifier of the item to update.
        updated_item (Item): The `Item` object with updated details.
        db_repo: Database repository dependency.

    Raises:
        DBNotAvailableError: If the database is not available.

    Returns:
        Item: The updated `Item` object, or `None` if not found.
    """
    if not db_repo.connected():
        raise DBNotAvailableError

    return db_repo.update_item(item_id, updated_item)


@router.delete("/items/{item_id}")
async def remove_item(
    item_id: int,
    db_repo: database.DatabaseRepository = fastapi.Depends(database.DatabaseRepository),
) -> None:
    """Delete an item from the inventory by its ID.

    Args:
        item_id (int): The unique identifier of the item to delete.
        db_repo: Database repository dependency.

    Raises:
        DBNotAvailableError: If the database is not available.

    Returns:
        bool: `True` if the item was successfully deleted, otherwise `False`.
    """
    if not db_repo.connected():
        raise DBNotAvailableError

    db_repo.delete_item(item_id)
