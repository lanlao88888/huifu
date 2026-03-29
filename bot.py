import logging
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# --- 1. 配置 ---
TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID_VAL = os.getenv("ADMIN_ID", "7934724103").strip()

# --- 2. 核心验证名单 (强制固定，直接修改这里) ---
VALID_GROUPS = ["88", "116", "117", "118", "100", "006", "168", "333", "A222", "B188"]

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- 3. 业务逻辑处理 ---
WAITING_GROUP_ID = 1
MAIN_MENU = [['人工客服', '资源对接'], ['自助验群', '纠纷仲裁']]
main_reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)

# 启动指令
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "您好，欢迎来到微担保服务中心，请点击下方对应的业务板块选择您要办理的业务😊",
        reply_markup=main_reply_markup
    )

# 触发自助验群
async def start_verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 请输入您需要验证的群编号，如：123、A112。")
    return WAITING_GROUP_ID

# 验证逻辑 (直接比对列表)
async def check_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip().upper()
    
    if user_input in VALID_GROUPS:
        res = f"✅ 查询结果：【{user_input}】\n该群为已查证的公群或专群，可放心交易。"
    else:
        res = f"❌ 查询结果：【{user_input}】\n未查证到该编号！注意⚠️是假群，请勿交易。"

    await update.message.reply_text(res, reply_markup=main_reply_markup)
    return ConversationHandler.END

# 关键词回复 (报备编号/人工客服等)
async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text: return

    # --- 找回来的“报备编号”功能 ---
    if "报备编号" in text:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("对接发货", url="https://t.me/install88"),
             InlineKeyboardButton("做单流程", url="https://t.me/c/2895181398/743")],
            [InlineKeyboardButton("微担保公群", url="https://t.me/weigq")]
        ])
        await update.message.reply_text(
            "手机拍照业务公群\n\n公群上压89999u\n\n1.进群必看操作流程\n2.公群禁言也可以正常结账",
            reply_markup=keyboard
        )
        return

    # 其他菜单按钮回复
    responses = {
        "人工客服": "正在分配人工客服，请耐心等待...",
        "资源对接": "请详细说明您需要对接的板块...",
        "纠纷仲裁": "请先描述您纠纷的内容及群号..."
    }
    if text in responses:
        await update.message.reply_text(responses[text])

# --- 4. 启动程序 ---
def main():
    if not TOKEN:
        print("错误: 未检测到 BOT_TOKEN")
        return
        
    app = Application.builder().token(TOKEN).build()
    
    # 验群对话处理器
    verify_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^自助验群$'), start_verify)],
        states={
            WAITING_GROUP_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_group_id)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(verify_handler)
    # 处理报备编号和其他文字回复
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))

    print("🚀 纯净固定名单版机器人已启动...")
    app.run_polling()

if __name__ == "__main__":
    main()
