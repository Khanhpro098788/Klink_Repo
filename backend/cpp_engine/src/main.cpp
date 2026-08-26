#include <iostream>
#include <memory>
#include <string>
#include <grpcpp/grpcpp.h>
#include "video_service_impl.h"

void RunServer() {
    std::string server_address("0.0.0.0:50051");
    video::VideoServiceImpl service;

    grpc::ServerBuilder builder;
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    builder.RegisterService(&service);

    std::unique_ptr<grpc::Server> server(builder.BuildAndStart());
    std::cout << "[C++ Server] gRPC C++ Server listening on " << server_address << std::endl;
    server->Wait();
}

int main() {
    RunServer();
    return 0;
}
