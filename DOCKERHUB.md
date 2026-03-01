# OpenClaw Monitor - Docker 部署

轻量级 OpenClaw 监控容器，支持 Web 界面和 Telegram 通知。

## 快速开始

### 方式一：Docker Hub（推荐）

```bash
# 拉取镜像
docker pull your-username/openclaw-monitor:latest

# 运行容器
docker run -d \
  --name openclaw-monitor \
  --restart unless-stopped \
  -p 8080:8080 \
  -e OPENCLAW_URL=http://YOUR_OPENCLAW_IP:18789 \
  -e OPENCLAW_GATEWAY=ws://YOUR_OPENCLAW_IP:18789 \
  -e TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN \
  -e TELEGRAM_CHAT_ID=YOUR_CHAT_ID \
  -v /path/to/data:/app/data \
  your-username/openclaw-monitor:latest
```

### 方式二：Docker Compose

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/openclaw-monitor.git
cd openclaw-monitor

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 构建并运行
docker-compose up -d
```

### 方式三：从源码构建

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/openclaw-monitor.git
cd openclaw-monitor

# 构建镜像
docker build -t openclaw-monitor .

# 运行容器
docker run -d \
  --name openclaw-monitor \
  --restart unless-stopped \
  -p 8080:8080 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  openclaw-monitor
```

## 环境变量

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| OPENCLAW_URL | OpenClaw Dashboard 地址 | - | 是 |
| OPENCLAW_GATEWAY | OpenClaw Gateway 地址 | - | 是 |
| TELEGRAM_BOT_TOKEN | Telegram Bot Token | - | 否 |
| TELEGRAM_CHAT_ID | Telegram Chat ID | - | 否 |
| CHECK_INTERVAL | 检查间隔（秒） | 60 | 否 |
| HISTORY_DAYS | 历史数据保留天数 | 7 | 否 |

## Telegram 通知配置

查看 [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) 了解如何配置 Telegram 通知。

## Unraid 部署

查看 [UNRAID_DEPLOY.md](UNRAID_DEPLOY.md) 了解如何在 Unraid 上部署。

## 访问监控界面

部署完成后，访问：`http://YOUR_IP:8080`

## 功能特性

- ✅ 实时监控 OpenClaw 状态
- ✅ Web 可视化界面
- ✅ Telegram 状态通知
- ✅ 历史数据记录
- ✅ 响应时间监控
- ✅ 24小时在线率统计

## 许可证

MIT License
