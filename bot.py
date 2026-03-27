import requests
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "你的Bot Token")  # 从环境变量读取，或者直接填

def send_message_with_inline_buttons(chat_id):
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
    requests.post(url, json=payload)

last_id = 0
print("机器人已启动，等待消息...")

while True:
    try:
        updates = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", 
                              params={"offset": last_id + 1, "timeout": 30}).json()
        
        for update in updates.get("result", []):
            last_id = update["update_id"]
            msg = update.get("message", {})
            text = msg.get("text", "")
            
            if text.startswith("报备编号"):
                send_message_with_inline_buttons(msg["chat"]["id"])
                print(f"已回复: {text}")
        
        time.sleep(1)
    except Exception as e:
        print(f"错误: {e}")
        time.sleep(5)
