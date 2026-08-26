from datetime import timedelta
from temporalio import workflow

# Import activities
with workflow.unsafe.imports_passed_through():
    from app.temporal_worker.activities import (
        download_assets,
        trigger_cpp_engine,
        upload_to_cdn,
        charge_credit,
        refund_credit
    )

@workflow.defn
class VideoRenderWorkflow:
    @workflow.run
    async def run(self, task_id: str, script_id: str, credit_amount: int) -> str:
        # Saga pattern tracking
        is_charged = False
        
        # Define activity retry policy
        retry_policy = {
            "initial_interval": timedelta(seconds=2),
            "backoff_coefficient": 2.0,
            "maximum_attempts": 3,
        }
        
        try:
            # 1. Charge credits temporarily (ACID Transaction)
            await workflow.execute_activity(
                charge_credit,
                args=[task_id, credit_amount],
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=retry_policy
            )
            is_charged = True
            
            # 2. Download raw assets (Video and audio)
            download_result = await workflow.execute_activity(
                download_assets,
                args=[task_id, script_id],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )
            
            # 3. Trigger C++ gRPC Core Engine
            render_result = await workflow.execute_activity(
                trigger_cpp_engine,
                args=[
                    task_id,
                    script_id,
                    download_result["video_local_path"],
                    download_result["audio_local_path"]
                ],
                start_to_close_timeout=timedelta(minutes=15),
                retry_policy=retry_policy
            )
            
            # 4. Upload finished video to GCS / CDN
            cdn_result = await workflow.execute_activity(
                upload_to_cdn,
                args=[task_id, render_result["output_local_path"]],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )
            
            return cdn_result["result_url"]
            
        except Exception as e:
            # Compensating transaction in case of failure
            if is_charged:
                await workflow.execute_activity(
                    refund_credit,
                    args=[task_id, credit_amount],
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=retry_policy
                )
            raise e
