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

    return { WebsiteURL: service.statuses[0].url };
  },
});
