import requests
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# 从环境变量获取Bot Token
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")


def send_message_with_inline_buttons(chat_id):
    """发送带内联按钮的消息"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "对接发货", "url": "https://t.me/install88"},
                {"text": "做单流程", "url": "https://t.me/c/2895181398/743"}
            ],
            [
                {"text": "微担保公群", "url": "https://t.me/weigq"}
            ]
        ]
    }

    payload = {
        "chat_id": chat_id,
        "text": "手机拍照业务公群\n\n公群上压89999u\n\n1.进群必看置顶操作流程\n\n2.公群禁言也可以正常结账\n结账时像对接人员私信自己的结账设备编号",
        "reply_markup": keyboard,
        "parse_mode": "HTML"
    }

    response = requests.post(url, json=payload)
    return response.json()


@app.route('/webhook', methods=['POST'])
def webhook():
    """处理Telegram的webhook回调"""
    update = request.get_json()
    
    if update and 'message' in update:
        message = update['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        # 检查消息前四个字是否为"报备编号"
        if text.startswith('报备编号'):
            send_message_with_inline_buttons(chat_id)
    
    return jsonify({"status": "ok"})


@app.route('/')
def index():
    return "Telegram Bot is running!"


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
