import requests


def send_message_with_inline_buttons(bot_token, chat_id):
    """发送带内联按钮的消息"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

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

    response = requests.post(url, json=payload)
    return response.json()


def send_message_with_reply_keyboard(bot_token, chat_id):
    """发送带自定义回复键盘的消息"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # 自定义回复键盘配置
    keyboard = {
        "keyboard": [
            [
                {"text": "📦 查询订单"},
                {"text": "👤 个人中心"}
            ],
            [
                {"text": "📞 联系客服"},
                {"text": "ℹ️ 帮助"}
            ]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
        "input_field_placeholder": "选择菜单选项..."
    }

    payload = {
        "chat_id": chat_id,
        "text": "请选择菜单选项：",
        "reply_markup": keyboard
    }

    response = requests.post(url, json=payload)
    return response.json()


def send_media_with_buttons(bot_token, chat_id):
    """发送带按钮的图片"""
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "⬅️ 上一张", "callback_data": "prev"},
                {"text": "➡️ 下一张", "callback_data": "next"}
            ],
            [
                {"text": "❤️ 喜欢", "callback_data": "like"},
                {"text": "💬 评论", "callback_data": "comment"}
            ]
        ]
    }

    payload = {
        "chat_id": chat_id,
        "photo": "https://example.com/image.jpg",  # 图片URL或file_id
        "caption": "这是一张美丽的图片",
        "reply_markup": keyboard
    }

    response = requests.post(url, json=payload)
    return response.json()


# 使用示例
if __name__ == "__main__":
    BOT_TOKEN = "8635376785:AAEtmHoWh2kJAeGD43HCF5vHCZRrwQZ265A"
    CHAT_ID = "-1002678968162"  # 可以是用户ID或群组ID

    # 发送消息
    result = send_message_with_inline_buttons(BOT_TOKEN, CHAT_ID)
    print(result)
