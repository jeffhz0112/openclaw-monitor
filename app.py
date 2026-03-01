#!/usr/bin/env python3
"""
OpenClaw Monitor - 轻量级监控容器
监控 OpenClaw 的运行状态、响应时间，并通过 Telegram 发送通知
"""

import os
import time
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from threading import Thread
import requests
import psutil
from flask import Flask, render_template, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
import telegram

# 配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 从环境变量读取配置
OPENCLAW_URL = os.getenv('OPENCLAW_URL', 'http://192.168.31.69:18789')
OPENCLAW_GATEWAY = os.getenv('OPENCLAW_GATEWAY', 'ws://192.168.31.69:18789')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 60))  # 默认60秒检查一次
HISTORY_DAYS = int(os.getenv('HISTORY_DAYS', 7))  # 保留7天历史数据

# 数据库初始化
DB_PATH = '/app/data/monitor.db'

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 创建状态记录表
    c.execute('''
        CREATE TABLE IF NOT EXISTS status_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL,
            response_time REAL,
            dashboard_status TEXT,
            gateway_status TEXT,
            error_message TEXT
        )
    ''')
    
    # 创建索引
    c.execute('''
        CREATE INDEX IF NOT EXISTS idx_timestamp 
        ON status_logs(timestamp)
    ''')
    
    conn.commit()
    conn.close()

def check_openclaw_status():
    """检查 OpenClaw 状态"""
    result = {
        'timestamp': datetime.now().isoformat(),
        'status': 'unknown',
        'response_time': None,
        'dashboard_status': 'unknown',
        'gateway_status': 'unknown',
        'error_message': None
    }
    
    # 检查 Dashboard HTTP 状态
    try:
        start_time = time.time()
        response = requests.get(
            f"{OPENCLAW_URL}/",
            timeout=10,
            headers={'User-Agent': 'OpenClaw-Monitor/1.0'}
        )
        result['response_time'] = round((time.time() - start_time) * 1000, 2)  # 毫秒
        
        if response.status_code == 200:
            result['dashboard_status'] = 'online'
        else:
            result['dashboard_status'] = f'error_{response.status_code}'
            
    except requests.exceptions.ConnectionError:
        result['dashboard_status'] = 'offline'
        result['error_message'] = 'Dashboard 连接失败'
    except requests.exceptions.Timeout:
        result['dashboard_status'] = 'timeout'
        result['error_message'] = 'Dashboard 响应超时'
    except Exception as e:
        result['dashboard_status'] = 'error'
        result['error_message'] = str(e)
    
    # 检查 Gateway WebSocket 状态（简化版，只检查端口连通性）
    try:
        # 提取 Gateway 端口
        import re
        port_match = re.search(r':(\d+)', OPENCLAW_GATEWAY)
        if port_match:
            port = int(port_match.group(1))
            # 使用 socket 检查端口
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            host = OPENCLAW_GATEWAY.split('://')[1].split(':')[0]
            result_socket = sock.connect_ex((host, port))
            if result_socket == 0:
                result['gateway_status'] = 'online'
            else:
                result['gateway_status'] = 'offline'
            sock.close()
        else:
            result['gateway_status'] = 'unknown'
    except Exception as e:
        result['gateway_status'] = 'error'
        logger.error(f"Gateway check failed: {e}")
    
    # 综合状态判断
    if result['dashboard_status'] == 'online' and result['gateway_status'] == 'online':
        result['status'] = 'online'
    elif result['dashboard_status'] == 'offline' and result['gateway_status'] == 'offline':
        result['status'] = 'offline'
    else:
        result['status'] = 'degraded'
    
    return result

def save_status_to_db(status_data):
    """保存状态到数据库"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO status_logs 
        (timestamp, status, response_time, dashboard_status, gateway_status, error_message)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        status_data['timestamp'],
        status_data['status'],
        status_data['response_time'],
        status_data['dashboard_status'],
        status_data['gateway_status'],
        status_data['error_message']
    ))
    
    conn.commit()
    conn.close()

def clean_old_data():
    """清理旧数据"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    cutoff_date = datetime.now() - timedelta(days=HISTORY_DAYS)
    c.execute('DELETE FROM status_logs WHERE timestamp < ?', (cutoff_date,))
    
    conn.commit()
    conn.close()

async def send_telegram_notification(message):
    """发送 Telegram 通知"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram 配置不完整，跳过通知")
        return
    
    try:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode='Markdown'
        )
        logger.info(f"Telegram 通知已发送: {message[:50]}...")
    except Exception as e:
        logger.error(f"发送 Telegram 通知失败: {e}")

def notify_status_change(old_status, new_status):
    """状态变化时发送通知"""
    if old_status == new_status:
        return
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if new_status == 'offline':
        message = f"🔴 *OpenClaw 离线警报*\n\n"
        message += f"时间: {timestamp}\n"
        message += f"状态: {old_status} → {new_status}\n"
        message += f"Dashboard: {OPENCLAW_URL}\n"
        message += f"请立即检查 Mac mini 和 OpenClaw 服务！"
    elif new_status == 'online' and old_status == 'offline':
        message = f"🟢 *OpenClaw 恢复正常*\n\n"
        message += f"时间: {timestamp}\n"
        message += f"状态: {old_status} → {new_status}\n"
        message += f"Dashboard: {OPENCLAW_URL}\n"
        message += f"服务已恢复正常运行。"
    elif new_status == 'degraded':
        message = f"🟡 *OpenClaw 降级警告*\n\n"
        message += f"时间: {timestamp}\n"
        message += f"状态: {old_status} → {new_status}\n"
        message += f"Dashboard: {OPENCLAW_URL}\n"
        message += f"部分服务可能不可用，请检查。"
    else:
        return
    
    # 异步发送通知
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_telegram_notification(message))
    loop.close()

# 全局变量存储上一次状态
last_status = None

def monitor_job():
    """定时监控任务"""
    global last_status
    
    logger.info("执行监控检查...")
    
    # 检查状态
    status_data = check_openclaw_status()
    
    # 保存到数据库
    save_status_to_db(status_data)
    
    # 状态变化通知
    if last_status is not None and last_status != status_data['status']:
        notify_status_change(last_status, status_data['status'])
    
    last_status = status_data['status']
    
    logger.info(f"状态: {status_data['status']}, 响应时间: {status_data['response_time']}ms")

# Flask 路由
@app.route('/')
def index():
    """主页"""
    return render_template('index.html',
                           openclaw_url=OPENCLAW_URL,
                           check_interval=CHECK_INTERVAL)

@app.route('/api/status')
def api_status():
    """获取当前状态"""
    status = check_openclaw_status()
    return jsonify(status)

@app.route('/api/history')
def api_history():
    """获取历史数据"""
    hours = request.args.get('hours', 24, type=int)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    c.execute('''
        SELECT timestamp, status, response_time, dashboard_status, gateway_status
        FROM status_logs 
        WHERE timestamp > ? 
        ORDER BY timestamp ASC
    ''', (cutoff_time,))
    
    rows = c.fetchall()
    conn.close()
    
    data = {
        'timestamps': [row[0] for row in rows],
        'statuses': [row[1] for row in rows],
        'response_times': [row[2] if row[2] else 0 for row in rows],
        'dashboard_statuses': [row[3] for row in rows],
        'gateway_statuses': [row[4] for row in rows]
    }
    
    return jsonify(data)

@app.route('/api/stats')
def api_stats():
    """获取统计信息"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 最近24小时统计
    cutoff_time = datetime.now() - timedelta(hours=24)
    
    # 在线率
    c.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'online' THEN 1 ELSE 0 END) as online_count
        FROM status_logs 
        WHERE timestamp > ?
    ''', (cutoff_time,))
    
    row = c.fetchone()
    total = row[0]
    online_count = row[1]
    uptime_percent = round((online_count / total * 100), 2) if total > 0 else 0
    
    # 平均响应时间
    c.execute('''
        SELECT AVG(response_time) 
        FROM status_logs 
        WHERE timestamp > ? AND response_time IS NOT NULL
    ''', (cutoff_time,))
    
    result = c.fetchone()
    avg_response_time = round(result[0], 2) if result and result[0] else 0
    
    conn.close()
    
    return jsonify({
        'uptime_24h': uptime_percent,
        'avg_response_time': avg_response_time,
        'total_checks': total
    })

@app.route('/health')
def health():
    """健康检查端点"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    # 设置定时任务
    scheduler = BackgroundScheduler()
    scheduler.add_job(monitor_job, 'interval', seconds=CHECK_INTERVAL)
    scheduler.add_job(clean_old_data, 'interval', hours=24)  # 每天清理一次旧数据
    scheduler.start()
    
    logger.info(f"OpenClaw Monitor 启动")
    logger.info(f"监控地址: {OPENCLAW_URL}")
    logger.info(f"检查间隔: {CHECK_INTERVAL}秒")
    logger.info(f"Telegram 通知: {'已配置' if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID else '未配置'}")
    
    # 立即执行一次检查
    monitor_job()
    
    # 启动 Flask 应用
    app.run(host='0.0.0.0', port=8080, debug=False)
