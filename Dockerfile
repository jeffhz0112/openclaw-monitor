FROM python:3.11-slim

# 设置容器元数据
LABEL maintainer="OpenClaw Monitor"
LABEL description="Lightweight monitoring container for OpenClaw"
LABEL org.opencontainers.image.title="OpenClaw Monitor"
LABEL org.opencontainers.image.description="Real-time monitoring for OpenClaw with Telegram notifications"
LABEL org.opencontainers.image.icon="https://raw.githubusercontent.com/openclaw/openclaw/main/docs/public/apple-touch-icon.png"

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用文件
COPY . .

# 创建数据目录
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# 运行应用
CMD ["python", "app.py"]
