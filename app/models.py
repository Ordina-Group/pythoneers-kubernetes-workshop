from sqlalchemy import Column, Integer, String, Float
from pydantic import BaseModel
from typing import Optional
from app.database import Base


class ItemORM(Base):
    """
    SQLAlchemy ORM model representing an item in the inventory.

    Attributes:
        __tablename__ (str): The name of the database table, "inventory".
        id (Column): The primary key for the item, an integer.
        name (Column): The name of the item, a string with a maximum length of 20 characters.
        description (Column): A description of the item, a string with a maximum length of 100 characters.
        price (Column): The price of the item, stored as a floating-point number.
        quantity (Column): The quantity of the item in stock, an integer.
    """

    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=20), index=True)
    description = Column(String(length=100), index=True)
    price = Column(Float, index=True)
    quantity = Column(Integer, index=True)


class Item(BaseModel):
    """
    Pydantic model representing an item in the inventory.

    Attributes:
        id (int): The unique identifier of the item.
        name (str): The name of the item.
        description (Optional[str]): A brief description of the item. Defaults to None.
        price (float): The price of the item.
        quantity (int): The quantity of the item in stock.

    Config:
        from_attributes (bool): Configuration option to enable attribute-to-dictionary conversion from ORM instances.
    """

    id: int
    name: str
    description: Optional[str] = None
    price: float
    quantity: int

    class Config:
        from_attributes = True