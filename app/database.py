import contextlib
import os
import sqlalchemy
from app import models

# URL for the database connection. Defaults to a PostgreSQL URL if not set in environment variables.
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://user:password@localhost:5432/workshop-k8s"
)


class DatabaseRepository:
    """
    A repository for interacting with the database using SQLAlchemy.
    This class provides methods to manage database sessions, ensure tables exist,
    and CRUD operations for the 'Item' model.
    """

    @property
    def engine(self):
        """
        Creates and returns a SQLAlchemy engine connected to the database.

        Returns:
            sqlalchemy.engine.Engine: The SQLAlchemy engine for the database connection.
        """
        return sqlalchemy.create_engine(DATABASE_URL)

    @contextlib.contextmanager
    def session(self):
        """
        A context manager that provides a database session for querying and committing changes.

        This method ensures the database tables are created and provides a session to interact
        with the database. The session is automatically closed when the context manager exits.

        Yields:
            sqlalchemy.orm.Session: The database session for executing queries and transactions.
        """
        self.ensure_tables_are_created()
        SessionLocal = sqlalchemy.orm.sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def connected(self) -> bool:
        """
        Checks if the database connection is active.

        Tries to establish a connection with the database and returns True if successful,
        otherwise returns False.

        Returns:
            bool: True if the database connection is active, otherwise False.
        """
        try:
            with self.engine.connect():
                return True
        except sqlalchemy.exc.OperationalError:
            return False

    def ensure_tables_are_created(self) -> None:
        """
        Ensures that the database tables are created if they do not already exist.

        This method checks if the database connection is available, and then creates tables
        for all defined models if they do not exist.
        """
        with self.engine.connect() as connection:
            if not connection:
                return
            models.Base.metadata.create_all(bind=self.engine, checkfirst=True)

    def get_items(self):
        """
        Retrieves all items from the database.

        This method queries the database for all records in the 'Item' table and returns
        them as a list of `ItemORM` objects.

        Returns:
            list: A list of `ItemORM` objects representing the items in the database.
        """
        with self.session() as session:
            return session.query(models.ItemORM).all()

    def get_item(self, item_id):
        """
        Retrieves a single item from the database by its ID.

        Args:
            item_id (int): The ID of the item to retrieve.

        Returns:
            models.ItemORM: The item with the given ID, or None if not found.
        """
        with self.session() as session:
            return session.query(models.ItemORM).filter(models.ItemORM.id == item_id).first()

    def create_item(self, item: models.Item) -> models.Item:
        """
        Creates a new item in the database.

        Args:
            item (models.Item): The item to create, represented as an `Item` model object.

        Returns:
            models.Item: The created item.

        Raises:
            ValueError: If an item with the same ID already exists in the database.
        """
        if self.item_exists(item.id):
            raise ValueError(f"Item with id {item.id} already exists")
        with self.session() as session:
            db_item = models.ItemORM(**item.model_dump())
            session.add(db_item)
            session.commit()
            session.refresh(db_item)
            return item

    def item_exists(self, item_id: int) -> bool:
        """
        Checks if an item with the given ID exists in the database.

        Args:
            item_id (int): The ID of the item to check for existence.

        Returns:
            bool: True if the item exists, otherwise False.
        """
        with self.session() as session:
            return session.query(models.ItemORM).filter(models.ItemORM.id == item_id).first() is not None

    def update_item(self, item_id: int, item: models.Item) -> models.Item:
        """
        Updates an existing item in the database.

        Args:
            item_id (int): The ID of the item to update.
            item (models.Item): The item data to update, represented as an `Item` model object.

        Returns:
            models.Item: The updated item.
        """
        with self.session() as session:
            db_item = (
                session.query(models.ItemORM)
                .filter(models.ItemORM.id == item_id)
                .first()
            )
            for attr, value in item.model_dump().items():
                setattr(db_item, attr, value)
            session.commit()
            session.refresh(db_item)
            return item

    def delete_item(self, item_id: int):
        """
        Deletes an item from the database.

        Args:
            item_id (int): The ID of the item to delete.

        Returns:
            models.ItemORM: The deleted item object.
        """
        with self.session() as session:
            db_item = (
                session.query(models.ItemORM)
                .filter(models.ItemORM.id == item_id)
                .first()
            )
            session.delete(db_item)
            session.commit()
            return db_item
