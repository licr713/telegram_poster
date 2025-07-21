import os
import logging
import requests
from telethon import TelegramClient, events

# 启动时交互输入敏感配置
API_ID = int(input('请输入 API_ID: '))
API_HASH = input('请输入 API_HASH: ')
N8N_WEBHOOK_URL = input('请输入 N8N_WEBHOOK_URL: ')
TARGET_CHANNEL = input('请输入要监听的频道用户名（如 Financial_Express）: ')
SESSION_NAME = os.getenv('SESSION_NAME', 'telegram_listener')

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)
logger = logging.getLogger(__name__)

# 初始化 Telethon 客户端
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

@client.on(events.NewMessage(chats=f'@{TARGET_CHANNEL}'))
async def handler(event):
    logger.info(f"捕获到新消息: {event.id}")
    try:
        channel_username = event.chat.username if event.chat and hasattr(event.chat, 'username') else TARGET_CHANNEL
        data = {
            'text': event.raw_text,
            'message_id': event.id,
            'channel_username': channel_username,
            'link': f"https://t.me/{channel_username}/{event.id}"
        }
        try:
            response = requests.post(N8N_WEBHOOK_URL, json=data, timeout=10)
            if response.status_code == 200:
                logger.info(f"消息 {event.id} 已成功发送到 n8n Webhook")
            else:
                logger.error(f"Webhook 响应异常: 状态码 {response.status_code}, 内容: {response.text}")
        except Exception as e:
            logger.error(f"发送到 n8n Webhook 时发生异常: {e}")
    except Exception as e:
        logger.error(f"处理消息时发生异常: {e}")

if __name__ == '__main__':
    logger.info(f"脚本启动，正在监听频道 @{TARGET_CHANNEL} ...")
    with client:
        client.run_until_disconnected() 