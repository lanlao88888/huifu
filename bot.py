import logging
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# --- 1. 配置 ---
TOKEN = os.getenv("BOT_TOKEN", "")
# 确保名单里全是字符串格式
VALID_GROUPS = ["88", "116", "117", "118", "100", "006", "168", "333", "A222", "B188"]

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- 2. 业务逻辑 ---
WAITING_GROUP_ID = 1
MAIN_MENU = [['人工客服', '资源对接'], ['自助验群', '纠纷仲裁']]
main_reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)

# 报备编号的具体内容函数
async def send_baobei_info(update: Update):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("对接发货", url="https://t.me/install88"),
         InlineKeyboardButton("做单流程", url="https://t.me/c/2895181398/743")],
        [InlineKeyboardButton("微担保公群", url="https://t.me/weigq")]
    ])
    await update.message.reply_text(
        "手机拍照业务公群\n\n公群上压89999u\n\n1.进群必看操作流程\n2.公群禁言也可以正常结账",
        reply_markup=keyboard
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("您好，欢迎来到微担保服务中心 😊", reply_markup=main_reply_markup)

async def start_verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 请输入您需要验证的群编号：")
    return WAITING_GROUP_ID

async def check_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip().upper()
    
    # 关键修复：如果在验群状态下输入了“报备编号”，直接跳出并回复
    if "报备编号" in user_input:
        await send_baobei_info(update)
        return ConversationHandler.END

    # 检查名单
    if user_input in VALID_GROUPS:
        res = f"✅ 查询结果：【{user_input}】\n该群为已验证公群，请放心交易。"
    else:
        res = f"❌ 查询结果：【{user_input}】\n未查证到该编号！注意假群。"

    await update.message.reply_text(res, reply_markup=main_reply_markup)
    return ConversationHandler.END

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "报备编号" in text:
        await send_baobei_info(update)
    elif text == "人工客服":
        await update.message.reply_text("正在转接人工...")
    # 其他菜单处理...

def main():
    app = Application.builder().token(TOKEN).build()
    
    verify_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^自助验群$'), start_verify)],
        states={
            WAITING_GROUP_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_group_id)],
        },
        fallbacks=[CommandHandler("start", start)],
        # 允许在等待编号时处理其他指令
        allow_reentry=True 
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(verify_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    app.run_polling()

if __name__ == "__main__":
    main()
