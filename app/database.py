import contextlib
import os
import sqlalchemy
from app import models

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://user:password@localhost:5432/workshop-k8s"
)


class DatabaseRepository:
    @property
    def engine(self):
        return sqlalchemy.create_engine(DATABASE_URL)

    @contextlib.contextmanager
    def session(self):
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
        try:
            with self.engine.connect():
                return True
        except sqlalchemy.exc.OperationalError:
            return False

    def ensure_tables_are_created(self) -> None:
        # only create table if the database is available
        with self.engine.connect() as connection:
            if not connection:
                return
            models.Base.metadata.create_all(bind=self.engine, checkfirst=True)

    def get_items(self):
        with self.session() as session:
            return session.query(models.ItemORM).all()

    def get_item(self, item_id):
        with self.session() as session:
            return session.query(models.ItemORM).filter(models.ItemORM.id == item_id).first()

    def create_item(self, item: models.Item) -> models.Item:
        with self.session() as session:
            db_item = models.ItemORM(**item.model_dump())
            session.add(db_item)
            session.commit()
            session.refresh(db_item)
            return item

    def update_item(self, item_id: int, item: models.Item) -> models.Item:
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
        with self.session() as session:
            db_item = (
                session.query(models.ItemORM)
                .filter(models.ItemORM.id == item_id)
                .first()
            )
            session.delete(db_item)
            session.commit()
            return db_item
