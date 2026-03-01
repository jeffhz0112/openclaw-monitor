# Unraid 部署指南

## 快速部署步骤

### 1. 上传文件到 NAS

将整个 `openclaw-monitor` 文件夹上传到 Unraid，例如：
```
/mnt/user/appdata/openclaw-monitor/
```

### 2. SSH 登录到 Unraid

```bash
ssh root@192.168.31.161
```

### 3. 进入项目目录

```bash
cd /mnt/user/appdata/openclaw-monitor
```

### 4. 配置环境变量（可选）

如果需要 Telegram 通知，编辑 `.env` 文件：
```bash
nano .env
```

填入你的 Telegram Bot Token 和 Chat ID。

### 5. 启动容器

```bash
docker compose up -d
```

或者使用传统命令：
```bash
docker build -t openclaw-monitor .
docker run -d \
  --name openclaw-monitor \
  --restart unless-stopped \
  -p 8080:8080 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  openclaw-monitor
```

### 6. 访问监控界面

浏览器打开：`http://192.168.31.161:8080`

## Unraid WebUI 配置（可选）

如果你想在 Unraid Docker 页面管理：

1. **添加容器**
   - Name: `openclaw-monitor`
   - Repository: 自己构建或上传镜像
   - Network: `bridge`
   - Port: `8080:8080`

2. **环境变量**
   - `OPENCLAW_URL`: `http://192.168.31.69:18789`
   - `OPENCLAW_GATEWAY`: `ws://192.168.31.69:18789`
   - `TELEGRAM_BOT_TOKEN`: 你的 token（可选）
   - `TELEGRAM_CHAT_ID`: 你的 chat ID（可选）

3. **存储映射**
   - `/mnt/user/appdata/openclaw-monitor/data` → `/app/data`

## 故障排除

### 查看日志
```bash
docker logs openclaw-monitor
```

### 查看容器状态
```bash
docker ps | grep openclaw-monitor
```

### 重启容器
```bash
docker restart openclaw-monitor
```

### 停止容器
```bash
docker stop openclaw-monitor
```

### 删除容器
```bash
docker rm -f openclaw-monitor
```

## 防火墙设置

如果无法访问监控界面，检查 Unraid 防火墙：
```bash
# 查看防火墙状态
ufw status

# 允许端口 8080
ufw allow 8080/tcp
```

## 自动启动

Docker 容器配置了 `restart: unless-stopped`，会在系统启动时自动运行。

## 监控目标

- **Mac mini**: `192.168.31.69`
- **OpenClaw Dashboard**: `http://192.168.31.69:18789`
- **OpenClaw Gateway**: `ws://192.168.31.69:18789`

## 更新监控容器

```bash
cd /mnt/user/appdata/openclaw-monitor
docker compose down
docker compose build --no-cache
docker compose up -d
```
