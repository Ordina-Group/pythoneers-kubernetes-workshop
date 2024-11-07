import pydantic
import sqlalchemy.orm
import sqlalchemy


class Base(sqlalchemy.orm.DeclarativeBase):
    """Declarative base class for SQLAlchemy ORM models."""


class ItemORM(Base):
    """
    SQLAlchemy ORM model representing an item in the inventory.

    Attributes:
        __tablename__ (str): The name of the database table, "inventory".
        id (sqlalchemy.Column): The primary key for the item, an integer.
        name (sqlalchemy.Column): The name of the item, a string with a maximum length of 20 characters.
        description (sqlalchemy.Column): A description of the item, a string with a maximum length of 100 characters.
        price (sqlalchemy.Column): The price of the item, stored as a floating-point number.
        quantity (sqlalchemy.Column): The quantity of the item in stock, an integer.
    """

    __tablename__ = "inventory"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String(length=20), index=True)
    description = sqlalchemy.Column(sqlalchemy.String(length=100), index=True)
    price = sqlalchemy.Column(sqlalchemy.Float, index=True)
    quantity = sqlalchemy.Column(sqlalchemy.Integer, index=True)


class Item(pydantic.BaseModel):
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
    description: str | None = None
    price: float
    quantity: int

    class Config:
        from_attributes = True
