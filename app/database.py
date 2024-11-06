import os
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:password@localhost:5432/workshop-k8s")

# Attempt to create the SQLAlchemy engine and session
try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    print(f"Database URL: {DATABASE_URL}")

    # If the connection is successful, set this flag to True
    db_available = True

except exc.SQLAlchemyError as e:
    print(f"Database connection failed: {e}")
    db_available = False
