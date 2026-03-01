# Telegram 通知配置指南

本指南帮助你配置 Telegram 通知，以便在 OpenClaw 状态变化时接收告警。

## 步骤 1: 创建 Telegram Bot

1. **打开 Telegram**，搜索 `@BotFather`

2. **创建新 Bot**
   ```
   /newbot
   ```

3. **设置 Bot 名称**
   - Bot 名称（显示名称）：例如 `OpenClaw Monitor`
   - Bot 用户名（必须以 `bot` 结尾）：例如 `openclaw_monitor_bot`

4. **保存 Bot Token**
   - BotFather 会返回类似这样的消息：
     ```
     Done! Congratulations on your new bot...
     Use this token to access the HTTP API:
     1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
     ```
   - 保存这个 Token，格式为：`1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

## 步骤 2: 获取 Chat ID

### 方法一：通过 API 获取（推荐）

1. **先向你的 Bot 发送一条消息**
   - 在 Telegram 中找到你刚创建的 Bot
   - 发送任意消息，例如：`/start`

2. **获取 Chat ID**
   - 在浏览器中访问以下 URL（替换 `<YOUR_BOT_TOKEN>` 为你的实际 Token）：
     ```
     https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
     ```
   
   - 例如：
     ```
     https://api.telegram.org/bot1234567890:ABCdefGHIjklMNOpqrsTUVwxyz/getUpdates
     ```

3. **查找 Chat ID**
   - 在返回的 JSON 数据中，找到 `chat.id` 字段：
     ```json
     {
       "ok": true,
       "result": [{
         "message": {
           "chat": {
             "id": 123456789,
             "first_name": "Your Name",
             "type": "private"
           }
         }
       }]
     }
     ```
   - 这个 `id` 就是你的 Chat ID（例如：`123456789`）

### 方法二：使用 @userinfobot

1. **在 Telegram 中搜索 `@userinfobot`**
2. **发送任意消息**
3. **它会回复你的 Chat ID**

## 步骤 3: 配置环境变量

编辑 `.env` 文件：

```bash
# Telegram Bot Token（从步骤 1 获取）
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Telegram Chat ID（从步骤 2 获取）
TELEGRAM_CHAT_ID=123456789
```

## 步骤 4: 重启监控容器

```bash
docker-compose restart
```

## 步骤 5: 测试通知

等待状态变化，或手动停止 OpenClaw 服务进行测试。

## 通知示例

### 🔴 离线警报
```
🔴 OpenClaw 离线警报

时间: 2026-02-28 23:45:00
状态: online → offline
Dashboard: http://192.168.31.69:18789
请立即检查 Mac mini 和 OpenClaw 服务！
```

### 🟢 恢复通知
```
🟢 OpenClaw 恢复正常

时间: 2026-02-28 23:50:00
状态: offline → online
Dashboard: http://192.168.31.69:18789
服务已恢复正常运行。
```

### 🟡 降级警告
```
🟡 OpenClaw 降级警告

时间: 2026-02-28 23:55:00
状态: online → degraded
Dashboard: http://192.168.31.69:18789
部分服务可能不可用，请检查。
```

## 故障排除

### 问题：收不到通知

1. **检查 Bot Token 和 Chat ID 是否正确**
   ```bash
   # 查看 .env 文件
   cat .env | grep TELEGRAM
   ```

2. **确认容器已重启**
   ```bash
   docker-compose restart
   ```

3. **检查容器日志**
   ```bash
   docker-compose logs -f | grep Telegram
   ```

4. **确认 Bot 有权限发送消息**
   - 确保你与 Bot 有过对话（发送过 `/start`）

### 问题：Token 格式错误

- 确保 Token 格式为：`数字:字母数字混合`
- 例如：`1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### 问题：Chat ID 错误

- Chat ID 应该是一个数字
- 个人聊天：通常是正数（如 `123456789`）
- 群组：通常是负数（如 `-100123456789`）

## 安全建议

1. **不要公开分享 Bot Token**
2. **将 `.env` 文件添加到 `.gitignore`**
3. **定期更换 Bot Token**（如果需要，可以通过 BotFather 重新生成）

## 高级配置

### 发送到群组

1. 将 Bot 添加到群组
2. 获取群组 Chat ID（通常是负数）
3. 更新 `.env` 文件中的 `TELEGRAM_CHAT_ID`

### 自定义通知消息

编辑 `app.py` 中的 `notify_status_change` 函数，自定义通知内容。

## 更多信息

- [Telegram Bot API 文档](https://core.telegram.org/bots/api)
- [python-telegram-bot 文档](https://python-telegram-bot.org/)
