#!/bin/bash

# OpenClaw Monitor 部署脚本
# 用于在 Unraid 上快速部署监控容器

set -e

echo "==================================="
echo "  OpenClaw Monitor 部署脚本"
echo "==================================="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker 未安装"
    echo "请先安装 Docker"
    exit 1
fi

echo "✅ Docker 已安装"

# 检查 docker-compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: docker-compose 未安装"
    echo "请先安装 docker-compose"
    exit 1
fi

echo "✅ docker-compose 已安装"
echo ""

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "📝 创建 .env 配置文件..."
    cp .env.example .env
    echo ""
    echo "⚠️  请编辑 .env 文件，配置以下信息："
    echo "   - OPENCLAW_URL: OpenClaw Dashboard 地址"
    echo "   - OPENCLAW_GATEWAY: OpenClaw Gateway 地址"
    echo "   - TELEGRAM_BOT_TOKEN: Telegram Bot Token（可选）"
    echo "   - TELEGRAM_CHAT_ID: Telegram Chat ID（可选）"
    echo ""
    echo "编辑完成后，请重新运行此脚本"
    exit 0
fi

echo "✅ .env 配置文件已存在"
echo ""

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p data
echo "✅ 数据目录创建成功"
echo ""

# 构建并启动容器
echo "🚀 构建 Docker 镜像..."
docker-compose build

echo ""
echo "🚀 启动监控容器..."
docker-compose up -d

echo ""
echo "⏳ 等待容器启动..."
sleep 10

# 检查容器状态
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "==================================="
    echo "✅ 部署成功！"
    echo "==================================="
    echo ""
    echo "📊 访问监控界面:"
    echo "   http://localhost:8080"
    echo ""
    echo "📝 查看日志:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 停止监控:"
    echo "   docker-compose down"
    echo ""
    echo "🔄 重启监控:"
    echo "   docker-compose restart"
    echo ""
    echo "==================================="
else
    echo ""
    echo "❌ 部署失败，请检查日志"
    echo "   docker-compose logs"
    exit 1
fi
