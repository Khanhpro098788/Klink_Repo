# Runbook: HTTP 5xx Error Alert Troubleshooting

This runbook describes the steps to troubleshoot and resolve a high rate of HTTP 5xx errors on the Klink AI Video Core Platform (`fastapi-demo-project`).

## Troubleshooting Steps

### 1. Check Service Logs
Go to **Google Cloud Logging -> Logs Explorer** and run the following query to identify the specific exception or error trace:
```query
resource.type="cloud_run_revision"
resource.labels.service_name="fastapi-demo-project"
severity>=ERROR
```
Review the JSON payload and traceback for any unhandled exceptions, database timeouts, or connection failures.

### 2. Verify Database Connection
If logs indicate database connection issues, check if the MongoDB cluster is up and accessible:
- Ensure the connection string in the environment variables is correct.
- Check MongoDB Atlas metrics for spikes in connections or operations.

### 3. Check Memory and CPU Saturation
In the **Cloud Run Console**, review the service metrics for CPU and Memory utilization:
- If Memory utilization is close to 100%, the service might be experiencing Out Of Memory (OOM) crashes.
- If CPU utilization is at 100%, request queuing might lead to gateway timeouts.
- Update `sst.config.ts` to increase CPU/Memory resources if necessary.

### 4. Rollback to Previous Stable Revision
If the errors started immediately after a deployment, rollback to the previous stable revision:
- Go to **Cloud Run -> fastapi-demo-project -> Revisions**.
- Select the previous revision and click **Manage Traffic**.
- Route 100% of traffic back to the previous stable revision.
