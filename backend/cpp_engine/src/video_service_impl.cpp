#include "video_service_impl.h"
#include <iostream>
#include <string>
#include <chrono>
#include <thread>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#else
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#define SOCKET int
#define INVALID_SOCKET -1
#define closesocket close
#endif

namespace video {

// Lightweight socket helper to publish progress to Redis (Localhost:6379) using RESP protocol
void publish_progress(const std::string& task_id, int progress) {
    std::string channel = "task_" + task_id + "_progress";
    std::string message = std::to_string(progress) + "%";
    
    // RESP format: *3\r\n$7\r\nPUBLISH\r\n$<channel_len>\r\n<channel>\r\n$<message_len>\r\n<message>\r\n
    std::string payload = "*3\r\n$7\r\nPUBLISH\r\n$" + std::to_string(channel.length()) + "\r\n" + channel + 
                          "\r\n$" + std::to_string(message.length()) + "\r\n" + message + "\r\n";

#ifdef _WIN32
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2,2), &wsaData) != 0) {
        return;
    }
#endif

    SOCKET sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == INVALID_SOCKET) {
#ifdef _WIN32
        WSACleanup();
#endif
        return;
    }

    sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(6379);
    
    if (inet_pton(AF_INET, "127.0.0.1", &server_addr.sin_addr) <= 0) {
        closesocket(sock);
#ifdef _WIN32
        WSACleanup();
#endif
        return;
    }

    if (connect(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) == 0) {
#ifdef _WIN32
        send(sock, payload.c_str(), static_cast<int>(payload.length()), 0);
#else
        write(sock, payload.c_str(), payload.length());
#endif
    }

    closesocket(sock);
#ifdef _WIN32
    WSACleanup();
#endif
}

grpc::Status VideoServiceImpl::Render(
    grpc::ServerContext* context,
    const RenderRequest* request,
    RenderResponse* response
) {
    std::cout << "[C++ Engine] Received render request for Task: " << request->task_id() << std::endl;
    std::cout << "[C++ Engine] Video Path: " << request->video_url() << std::endl;
    std::cout << "[C++ Engine] Audio Path: " << request->audio_url() << std::endl;
    
    auto start_time = std::chrono::high_resolution_clock::now();

    // 1. CUDA Context Initialization
    std::cout << "[CUDA] Initializing CUDA context on GPU device 0..." << std::endl;
    std::this_thread::sleep_for(std::chrono::milliseconds(500)); // Simulating CUDA Init

    // 2. Simulating NVDEC Video Decoding & Frame Loop
    std::cout << "[NVDEC] Loading hardware accelerated decoder for: " << request->video_url() << std::endl;
    
    int total_frames = 100;
    for (int frame = 1; frame <= total_frames; ++frame) {
        // Simulating processing frame
        // - Crop face Bounding Box (e.g. 256x256)
        // - Send to Triton Inference Server
        // - Blend back face onto original 4K frame using OpenCV Mat
        // - NVENC hardware encode
        std::this_thread::sleep_for(std::chrono::milliseconds(30)); // 30ms per frame simulation (33 fps)

        if (frame % 10 == 0 || frame == total_frames) {
            std::cout << "[C++ Engine] Processing: " << frame << "%" << std::endl;
            // Publish progress to Redis
            publish_progress(request->task_id(), frame);
        }
    }

    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time).count();

    // Output path allocation
    std::string output_file = request->video_url() + "_rendered.mp4";

    // Set Response
    response->set_task_id(request->task_id());
    response->set_success(true);
    response->set_output_url(output_file);
    response->set_processing_time_ms(duration);
    response->set_error_message("");

    std::cout << "[C++ Engine] Video generation completed. Output file saved to: " << output_file << std::endl;
    return grpc::Status::OK;
}

} // namespace video
