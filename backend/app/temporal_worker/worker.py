import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from app.config import settings
from app.core.database import db_manager
from app.temporal_worker.workflows import VideoRenderWorkflow
from app.temporal_worker.activities import (
    charge_credit,
    refund_credit,
    download_assets,
    trigger_cpp_engine,
    upload_to_cdn
)

async def main():
    # Connect MongoDB first
    db_manager.connect()
    print("Database connected for Temporal worker...")

    # Connect to Temporal server
    client = await Client.connect(
        settings.TEMPORAL_HOST,
        namespace=settings.TEMPORAL_NAMESPACE
    )
    print(f"Connected to Temporal server at {settings.TEMPORAL_HOST}")

    # Register workflow and activities
    worker = Worker(
        client,
        task_queue="video-render-task-queue",
        workflows=[VideoRenderWorkflow],
        activities=[
            charge_credit,
            refund_credit,
            download_assets,
            trigger_cpp_engine,
            upload_to_cdn
        ]
    )

    print("Temporal Worker is running and listening on queue 'video-render-task-queue'...")
    try:
        await worker.run()
    except asyncio.CancelledError:
        print("Temporal Worker shutting down...")
    finally:
        db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
