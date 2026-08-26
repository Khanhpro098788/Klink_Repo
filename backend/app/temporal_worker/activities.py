import os
from datetime import datetime
from bson import ObjectId
from temporalio import activity
from app.core.database import get_mongodb
from app.grpc_clients.cpp_client import VideoEngineClient

@activity.defn
async def charge_credit(task_id: str, credit_amount: int) -> bool:
    db = await get_mongodb()
    task = await db.video_tasks.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise ValueError(f"Task {task_id} not found")
        
    owner_id = task["owner_id"]
    # Atomically verify and charge credits
    result = await db.users.update_one(
        {"_id": owner_id, "credit_balance": {"$gte": credit_amount}},
        {"$inc": {"credit_balance": -credit_amount}}
    )
    
    if result.modified_count == 0:
        raise ValueError("Insufficient credits to run video generation task")
        
    # Log transaction
    await db.credit_logs.insert_one({
        "user_id": owner_id,
        "amount": -credit_amount,
        "reason": f"Debit for rendering task {task_id}",
        "created_at": datetime.utcnow()
    })
    return True

@activity.defn
async def refund_credit(task_id: str, credit_amount: int) -> bool:
    db = await get_mongodb()
    task = await db.video_tasks.find_one({"_id": ObjectId(task_id)})
    if not task:
        return False
        
    owner_id = task["owner_id"]
    # Refund credits
    await db.users.update_one(
        {"_id": owner_id},
        {"$inc": {"credit_balance": credit_amount}}
    )
    
    # Log refund transaction
    await db.credit_logs.insert_one({
        "user_id": owner_id,
        "amount": credit_amount,
        "reason": f"Refund for failed rendering task {task_id}",
        "created_at": datetime.utcnow()
    })
    return True

@activity.defn
async def download_assets(task_id: str, script_id: str) -> dict:
    db = await get_mongodb()
    script = await db.scripts.find_one({"_id": ObjectId(script_id)})
    if not script:
        raise ValueError(f"Script {script_id} not found")
        
    # Retrieve mock or reference URLs from database
    # In a real system, we'd fetch actual video/audio file assets details from DB and download them
    temp_dir = os.path.join(os.getcwd(), "scratch", "downloads", task_id)
    os.makedirs(temp_dir, exist_ok=True)
    
    # Simulate path allocation (Real local download path)
    video_local_path = os.path.join(temp_dir, "input_bg.mp4")
    audio_local_path = os.path.join(temp_dir, "input_voice.wav")
    
    # Write mock empty bytes or copy placeholders to paths
    with open(video_local_path, "wb") as f:
        f.write(b"MOCK VIDEO DATA")
    with open(audio_local_path, "wb") as f:
        f.write(b"MOCK AUDIO DATA")
        
    return {
        "video_local_path": video_local_path,
        "audio_local_path": audio_local_path
    }

@activity.defn
async def trigger_cpp_engine(
    task_id: str,
    script_id: str,
    video_local_path: str,
    audio_local_path: str
) -> dict:
    client = VideoEngineClient()
    
    # Call async gRPC C++ server
    # Since C++ expects these references, we pass local paths
    response = await client.render_video(
        task_id=task_id,
        script_id=script_id,
        video_url=video_local_path,
        audio_url=audio_local_path,
        resolution="1080p",
        delta_caching=True,
        auto_ducking=True
    )
    
    if not response or not response.success:
        error = response.error_message if response else "Unknown rendering error"
        raise RuntimeError(f"C++ Render Engine Error: {error}")
        
    return {
        "output_local_path": response.output_url
    }

@activity.defn
async def upload_to_cdn(task_id: str, output_local_path: str) -> dict:
    # In production, this uploads to Google Cloud Storage (GCS)
    # We will simulate the GCS URL mapped to Cloudflare CDN
    cdn_url = f"https://cdn.cloudflare.com/klink-output/{task_id}_output.mp4"
    
    # Update video task database status
    db = await get_mongodb()
    await db.video_tasks.update_one(
        {"_id": ObjectId(task_id)},
        {
            "$set": {
                "status": "completed",
                "progress": 100,
                "result_url": cdn_url,
                "completed_at": datetime.utcnow()
            }
        }
    )
    
    return {"result_url": cdn_url}
