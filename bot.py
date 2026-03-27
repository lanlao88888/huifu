import requests

# 配置你的Bot Token
BOT_TOKEN = "8635376785:AAEtmHoWh2kJAeGD43HCF5vHCZRrwQZ265A"  # 替换为你的bot token


def send_message_with_inline_buttons(chat_id):
    """发送带内联按钮的消息"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    # 内联键盘配置
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
