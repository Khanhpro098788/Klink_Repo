# Giai đoạn 1: Build mã nguồn React + Vite
FROM node:22-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Khai báo Build Argument để truyền URL Backend vào lúc build (Vite inject lúc compile)
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Giai đoạn 2: Khởi chạy Web Server bằng Nginx để serve file tĩnh
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# Cấu hình lại Nginx để hỗ trợ React Router (nếu có routing ở client) và chạy port 8080 phù hợp với Cloud Run
RUN echo 'server { listen 8080; location / { root /usr/share/nginx/html; index index.html; try_files $uri $uri/ /index.html; } }' > /etc/nginx/conf.d/default.conf
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
