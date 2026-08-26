#pragma once

#include <grpcpp/grpcpp.h>
#include "video_service.grpc.pb.h"

namespace video {

class VideoServiceImpl final : public VideoEngine::Service {
public:
    grpc::Status Render(
        grpc::ServerContext* context,
        const RenderRequest* request,
        RenderResponse* response
    ) override;
};

} // namespace video
