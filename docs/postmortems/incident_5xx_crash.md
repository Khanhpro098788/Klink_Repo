# Incident Postmortem: 5xx Crash Simulation

**Date**: 2026-08-28  
**Author**: Vo Van Khanh  
**Status**: Completed  

## Executive Summary
On 2026-08-28, a scheduled failure simulation was conducted to test the reliability of the Cloud Monitoring Alerting Policies on the `fastapi-demo-project` service. The system successfully detected the anomalous HTTP 5xx errors, triggered the alert, and notified the on-call engineer via email.

## Incident Timeline (UTC)
- **08:15**: Crash simulation initiated. 15 requests were sent to the `/crash` endpoint to simulate a server-side crash.
- **08:16**: The Alert Policy "Cloud Run 5xx Error Alert" registered the failures exceeding the threshold (count > 0 in 60s).
- **08:16**: Notification email received by the on-call engineer containing the alert details and a link to the runbook.
- **08:18**: Simulation ended. System returned to healthy status.

## Root Cause Analysis (5 Whys)
1. **Why did the service return HTTP 500?**  
   The `/crash` endpoint was triggered, raising an intentional `HTTPException`.
2. **Why was the endpoint triggered?**  
   It was executed as part of the scheduled failure testing simulation.
3. **Why did we simulate a failure?**  
   To verify that our alerting systems and notification channels are working properly.
4. **Why do we need verified alerts?**  
   To prevent undetected production downtime and ensure rapid response to system anomalies.
5. **Why do we want rapid response?**  
   To maintain the service SLA and minimize user impact during a real outage.

## Action Items
- Remove the `/crash` endpoint from the production environment (or wrap it with admin auth) to prevent unauthorized execution.
- Set up a staging environment for failure testing to avoid simulating crashes on the live service.
