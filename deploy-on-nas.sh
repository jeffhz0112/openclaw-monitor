#!/bin/bash

# OpenClaw Monitor 部署脚本（在 NAS 上执行）

echo "==================================="
echo "  OpenClaw Monitor 部署"
echo "==================================="
echo ""

# 进入项目目录
cd /mnt/user/appdata/openclaw-monitor

# 停止并删除旧容器
echo "停止旧容器..."
docker stop openclaw-monitor 2>/dev/null || true
docker rm openclaw-monitor 2>/dev/null || true

# 构建镜像
echo "构建 Docker 镜像..."
docker build -t openclaw-monitor . || {
    echo "镜像构建失败"
    exit 1
}

# 创建数据目录
mkdir -p data

# 启动容器
echo "启动容器..."
docker run -d \
  --name openclaw-monitor \
  --restart unless-stopped \
  -p 8080:8080 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  openclaw-monitor || {
    echo "容器启动失败"
    exit 1
}

# 等待容器启动
sleep 3

# 检查容器状态
if docker ps | grep -q openclaw-monitor; then
    echo ""
    echo "==================================="
    echo "✅ 部署成功！"
    echo "==================================="
    echo ""
    echo "监控界面: http://192.168.31.161:8080"
    echo ""
    docker logs openclaw-monitor | head -20
else
    echo ""
    echo "❌ 部署失败"
    docker logs openclaw-monitor
    exit 1
fi
