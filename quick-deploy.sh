#!/bin/bash

# Unraid 快速部署脚本
# 使用方法: bash quick-deploy.sh

set -e

echo "==================================="
echo "  OpenClaw Monitor - Unraid 部署"
echo "==================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 配置
NAS_IP="192.168.31.161"
NAS_USER="root"
NAS_PATH="/mnt/user/appdata/openclaw-monitor"
LOCAL_PATH="$(pwd)"

echo -e "${YELLOW}提示:${NC} 此脚本将部署监控容器到 Unraid NAS"
echo ""

# 检查 SSH 连接
echo -e "${YELLOW}[1/6]${NC} 检查 SSH 连接..."
if ! ssh -o ConnectTimeout=5 ${NAS_USER}@${NAS_IP} "echo '连接成功'" &> /dev/null; then
    echo -e "${RED}✗ SSH 连接失败${NC}"
    echo "请确保:"
    echo "  1. NAS 已启用 SSH"
    echo "  2. 网络连接正常"
    echo "  3. 可以使用 'ssh ${NAS_USER}@${NAS_IP}' 登录"
    exit 1
fi
echo -e "${GREEN}✓ SSH 连接成功${NC}"

# 创建远程目录
echo ""
echo -e "${YELLOW}[2/6]${NC} 创建远程目录..."
ssh ${NAS_USER}@${NAS_IP} "mkdir -p ${NAS_PATH}"
echo -e "${GREEN}✓ 目录创建成功${NC}"

# 上传文件
echo ""
echo -e "${YELLOW}[3/6]${NC} 上传文件到 NAS..."
scp -r ${LOCAL_PATH}/* ${LOCAL_PATH}/.env ${LOCAL_PATH}/.gitignore ${NAS_USER}@${NAS_IP}:${NAS_PATH}/ 2>/dev/null || true
echo -e "${GREEN}✓ 文件上传成功${NC}"

# 检查 Docker
echo ""
echo -e "${YELLOW}[4/6]${NC} 检查 Docker..."
if ! ssh ${NAS_USER}@${NAS_IP} "docker --version" &> /dev/null; then
    echo -e "${RED}✗ Docker 未安装${NC}"
    echo "请先在 Unraid 上安装 Docker"
    exit 1
fi
echo -e "${GREEN}✓ Docker 已安装${NC}"

# 构建镜像
echo ""
echo -e "${YELLOW}[5/6]${NC} 构建 Docker 镜像..."
ssh ${NAS_USER}@${NAS_IP} "cd ${NAS_PATH} && docker build -t openclaw-monitor ."
echo -e "${GREEN}✓ 镜像构建成功${NC}"

# 启动容器
echo ""
echo -e "${YELLOW}[6/6]${NC} 启动监控容器..."
ssh ${NAS_USER}@${NAS_IP} << 'ENDSSH'
cd /mnt/user/appdata/openclaw-monitor

# 停止旧容器（如果存在）
docker stop openclaw-monitor 2>/dev/null || true
docker rm openclaw-monitor 2>/dev/null || true

# 启动新容器
docker run -d \
  --name openclaw-monitor \
  --restart unless-stopped \
  -p 8080:8080 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  openclaw-monitor

# 等待容器启动
sleep 3

# 检查容器状态
if docker ps | grep -q openclaw-monitor; then
    echo "✓ 容器启动成功"
else
    echo "✗ 容器启动失败"
    docker logs openclaw-monitor
    exit 1
fi
ENDSSH

echo ""
echo "==================================="
echo -e "${GREEN}✅ 部署成功！${NC}"
echo "==================================="
echo ""
echo -e "📊 监控界面: ${GREEN}http://${NAS_IP}:8080${NC}"
echo ""
echo "📝 常用命令:"
echo "  查看日志: ssh ${NAS_USER}@${NAS_IP} 'docker logs -f openclaw-monitor'"
echo "  重启容器: ssh ${NAS_USER}@${NAS_IP} 'docker restart openclaw-monitor'"
echo "  停止容器: ssh ${NAS_USER}@${NAS_IP} 'docker stop openclaw-monitor'"
echo ""
echo "==================================="
