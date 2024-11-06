import os
import signal
import asyncio
from fastapi import APIRouter

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
