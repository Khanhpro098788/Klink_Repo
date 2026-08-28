/// <reference path="./.sst/platform/config.d.ts" />

export default $config({
  app(input) {
    return {
      name: "fastapi-demo",
      removal: input?.stage === "production" ? "retain" : "remove",
      protect: ["production"].includes(input?.stage),
      home: "local", // Sử dụng local state để bỏ qua AWS credentials
      providers: {
        gcp: {
          version: "8.41.1",            // Cấu hình rõ phiên bản gcp provider được tải
          project: "klink-deploy-2026", // Chỉ định project ID mặc định cho GCP Provider
        },
      },
    };
  },
  async run() {
    console.log(`Đang triển khai môi trường (stage): ${$app.stage}`);

    // Sử dụng dynamic import bên trong hàm run theo yêu cầu của SST v3
    const gcp = await import("@pulumi/gcp");

    // Khai báo dịch vụ Cloud Run và truyền rõ project ID vào tham số
    const service = new gcp.cloudrun.Service(`fastapi-service-${$app.stage}`, {
      project: "klink-deploy-2026",
      location: "asia-southeast1",
      template: {
        spec: {
          serviceAccountName: "cloudrun-runtime-sa@klink-deploy-2026.iam.gserviceaccount.com", // Chỉ định Service Account chạy lúc runtime
          containers: [{
            image: "asia-southeast1-docker.pkg.dev/klink-deploy-2026/fastapi-demo/fastapi-demo-project:latest",
            ports: [{ containerPort: 8080 }],
          }],
        },
      },
    });

    // Mở quyền public cho allUsers
    new gcp.cloudrun.IamMember(`public-access-${$app.stage}`, {
      project: "klink-deploy-2026",
      service: service.name,
      location: service.location,
      role: "roles/run.invoker",
      member: "allUsers",
    });

    // --- KHAI BÁO CÁC TÀI NGUYÊN MONITORING & ALERTING ---

    // 1. Kênh nhận cảnh báo qua Email
    const emailChannel = new gcp.monitoring.NotificationChannel(`email-channel-${$app.stage}`, {
      project: "klink-deploy-2026",
      type: "email",
      displayName: `Email Alert Channel (${$app.stage})`,
      labels: {
        email_address: "vovankhanh937@gmail.com",
      },
    });

    // 2. Cảnh báo lỗi HTTP 5xx (Lưu lượng lỗi > 0 trong 1 phút)
    const alert5xx = new gcp.monitoring.AlertPolicy(`alert-5xx-${$app.stage}`, {
      project: "klink-deploy-2026",
      displayName: `Cloud Run 5xx Error Alert (${$app.stage})`,
      combiner: "OR",
      conditions: [{
        displayName: "HTTP 5xx error count class",
        conditionThreshold: {
          filter: `resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count" AND metric.labels.response_code_class="5xx"`,
          duration: "60s",
          comparison: "COMPARISON_GT",
          thresholdValue: 0,
          aggregations: [{
            alignmentPeriod: "60s",
            perSeriesAligner: "ALIGN_RATE",
          }],
        },
      }],
      notificationChannels: [emailChannel.name],
      documentation: {
        content: `High rate of HTTP 5xx errors detected on Cloud Run service. Refer to runbook: docs/runbooks/alert_5xx.md`,
        mimeType: "text/markdown",
      },
    });

    // 3. Cảnh báo độ trễ Latency (p95 latency > 2000ms trong 5 phút)
    const alertLatency = new gcp.monitoring.AlertPolicy(`alert-latency-${$app.stage}`, {
      project: "klink-deploy-2026",
      displayName: `Cloud Run Latency p95 Alert (${$app.stage})`,
      combiner: "OR",
      conditions: [{
        displayName: "p95 Latency > 2000ms",
        conditionThreshold: {
          filter: `resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_latencies"`,
          duration: "300s",
          comparison: "COMPARISON_GT",
          thresholdValue: 2000, // 2000 ms
          aggregations: [{
            alignmentPeriod: "300s",
            perSeriesAligner: "ALIGN_PERCENTILE_95",
            crossSeriesReducer: "REDUCE_NONE",
          }],
        },
      }],
      notificationChannels: [emailChannel.name],
      documentation: {
        content: `Cloud Run p95 latency has exceeded 2000ms for 5 minutes. Check backend services and database connection.`,
        mimeType: "text/markdown",
      },
    });

    // 4. Bảng điều khiển hiệu năng (Performance Dashboard)
    const performanceDashboard = new gcp.monitoring.Dashboard(`performance-dashboard-${$app.stage}`, {
      project: "klink-deploy-2026",
      dashboardJson: JSON.stringify({
        displayName: `Cloud Run Performance Dashboard (${$app.stage})`,
        gridLayout: {
          columns: "2",
          widgets: [
            {
              title: "Request Volume (Traffic)",
              xyChart: {
                dataSets: [{
                  timeSeriesQuery: {
                    timeSeriesFilter: {
                      filter: `resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count"`,
                      aggregation: {
                        alignmentPeriod: "60s",
                        perSeriesAligner: "ALIGN_RATE"
                      }
                    }
                  }
                }]
              }
            },
            {
              title: "p95 Latency (Performance)",
              xyChart: {
                dataSets: [{
                  timeSeriesQuery: {
                    timeSeriesFilter: {
                      filter: `resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_latencies"`,
                      aggregation: {
                        alignmentPeriod: "60s",
                        perSeriesAligner: "ALIGN_PERCENTILE_95"
                      }
                    }
                  }
                }]
              }
            }
          ]
        }
      }),
    });

    return { 
      WebsiteURL: service.statuses[0].url,
      NotificationChannel: emailChannel.id,
      Alert5xxPolicy: alert5xx.id,
      AlertLatencyPolicy: alertLatency.id,
      DashboardName: performanceDashboard.id
    };
  },
});
