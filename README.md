# OpenClaw Monitor

[![Docker Build](https://github.com/jeffhz0112/openclaw-monitor/actions/workflows/docker-build.yml/badge.svg)](https://github.com/jeffhz0112/openclaw-monitor/actions/workflows/docker-build.yml)
[![CI](https://github.com/jeffhz0112/openclaw-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/jeffhz0112/openclaw-monitor/actions/workflows/ci.yml)
[![Docker Pulls](https://img.shields.io/docker/pulls/1520056819/openclaw-monitor.svg)](https://hub.docker.com/r/1520056819/openclaw-monitor)
[![License](https://img.shields.io/github/license/jeffhz0112/openclaw-monitor.svg)](LICENSE)

🦞 Lightweight monitoring container for OpenClaw with Telegram notifications and web interface.

![OpenClaw Monitor Dashboard](docs/dashboard.png)

## Features

- ✅ Real-time OpenClaw status monitoring
- ✅ Web-based dashboard
- ✅ Telegram notifications on status change
- ✅ Response time tracking
- ✅ 24-hour uptime statistics
- ✅ Historical data visualization
- ✅ Easy deployment with Docker

## Quick Start

### Using Docker Hub (Recommended)

```bash
# Pull the image
docker pull 1520056819/openclaw-monitor:latest

# Run the container
docker run -d \
  --name openclaw-monitor \
  --restart unless-stopped \
  -p 8080:8080 \
  -e OPENCLAW_URL=http://YOUR_OPENCLAW_IP:18789 \
  -e OPENCLAW_GATEWAY=ws://YOUR_OPENCLAW_IP:18789 \
  -e TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN \
  -e TELEGRAM_CHAT_ID=YOUR_CHAT_ID \
  -v /path/to/data:/app/data \
  1520056819/openclaw-monitor:latest
```

### Using Docker Compose

```bash
# Clone the repository
git clone https://github.com/jeffhz0112/openclaw-monitor.git
cd openclaw-monitor

# Configure environment variables
cp .env.example .env
# Edit .env file with your settings

# Start the container
docker-compose up -d
```

### Build from Source

```bash
# Clone the repository
git clone https://github.com/jeffhz0112/openclaw-monitor.git
cd openclaw-monitor

# Build the image
docker build -t openclaw-monitor .

# Run the container
docker run -d \
  --name openclaw-monitor \
  --restart unless-stopped \
  -p 8080:8080 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  openclaw-monitor
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| OPENCLAW_URL | OpenClaw Dashboard URL | - | ✅ |
| OPENCLAW_GATEWAY | OpenClaw Gateway URL | - | ✅ |
| TELEGRAM_BOT_TOKEN | Telegram Bot Token for notifications | - | ❌ |
| TELEGRAM_CHAT_ID | Telegram Chat ID for notifications | - | ❌ |
| CHECK_INTERVAL | Check interval in seconds | 60 | ❌ |
| HISTORY_DAYS | Days to keep historical data | 7 | ❌ |

### Telegram Notifications

See [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) for instructions on setting up Telegram notifications.

## Deployment

### Unraid

See [UNRAID_DEPLOY.md](UNRAID_DEPLOY.md) for Unraid deployment instructions.

### Docker Hub

See [DOCKERHUB.md](DOCKERHUB.md) for detailed Docker Hub deployment instructions.

## Access the Dashboard

After deployment, access the monitoring dashboard at:

```
http://YOUR_IP:8080
```

## Screenshots

### Dashboard
![Dashboard](docs/dashboard.png)

### Status Monitoring
![Status](docs/status.png)

## Monitoring Features

- **Real-time Status**: Monitor OpenClaw's online/offline status
- **Response Time**: Track HTTP response time in milliseconds
- **24h Uptime**: Calculate uptime percentage over 24 hours
- **History Charts**: Visualize historical data
- **Telegram Alerts**: Receive instant notifications on status changes

## Notification Types

- 🟢 **Online**: Service recovered
- 🔴 **Offline**: Service down
- 🟡 **Degraded**: Partial service failure

## Tech Stack

- **Backend**: Python 3.11, Flask
- **Database**: SQLite
- **Frontend**: Bootstrap 5, Chart.js
- **Monitoring**: APScheduler
- **Notifications**: python-telegram-bot

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Access at http://localhost:8080
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/jeffhz0112/openclaw-monitor/issues).

## Author

- **Jeff Huang** - [jeffhz0112](https://github.com/jeffhz0112)

## Acknowledgments

- OpenClaw - The amazing AI assistant framework
- All contributors and users

---

⭐ If this project helped you, please give it a star!
