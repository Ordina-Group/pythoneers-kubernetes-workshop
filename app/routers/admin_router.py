import os
import signal
import asyncio
from app.database import SessionLocal
from app.models import ItemORM
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/crash", description="Crash the entire service in 5 seconds.")
async def crash_app():
    """
    Initiates a countdown and crashes the application after 5 seconds.

    This endpoint can be used for testing purposes to simulate a crash.
    It will log a countdown message every second and, upon reaching
    zero, it will terminate the application by sending a SIGTERM signal.

    Raises:
        SystemExit: The application will exit upon receiving the SIGTERM signal.
    """
    # Countdown from 5 seconds before crashing
    for i in range(5, 0, -1):
        print(f"Application will crash in {i} seconds...")
        await asyncio.sleep(1)  # Wait for 1 second

    # Log the final crash message
    print("The application is about to crash!")
    os.kill(os.getpid(), signal.SIGTERM)


@router.get("/check-db-connection", description="Check and reconnect to the database if not connected.")
async def check_db_connection():
    """
    Checks the database connection and attempts to reconnect if not connected.

    Returns:
        List of items if the connection is successful.

    Raises:
        HTTPException: If the database connection could not be established.
    """
    try:
        # Try to create a session and execute a simple query
        db: Session = SessionLocal()
        items = db.query(ItemORM).all()
        db.close()  # Close the session after query execution
        return {"status": "success", "items": items}

    except OperationalError:
        # If the connection is not available, raise an HTTPException
        raise HTTPException(status_code=503, detail="Database connection is not available. Please try again later.")
    finally:
        db.close()
