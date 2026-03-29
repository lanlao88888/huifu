import logging
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# --- 1. 配置区域 ---
TOKEN = os.getenv("BOT_TOKEN", "")
# 这里的名单包含你要求的所有编号，确保全是字符串格式
VALID_GROUPS = [
    "88", "90", "91", "92", "116", "117", "118", "100", 
    "006", "168", "333", "A222", "B188"
]

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- 2. 核心功能函数 ---
WAITING_GROUP_ID = 1
MAIN_MENU = [['人工客服', '资源对接'], ['自助验群', '纠纷仲裁']]
main_reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)

# 统一的报备信息回复模板
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

# /start 指令
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "您好，欢迎来到微担保服务中心 😊\n请点击下方选择您要办理的业务。",
        reply_markup=main_reply_markup
    )

# 触发自助验群
async def start_verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 请输入您需要验证的群编号：")
    return WAITING_GROUP_ID

# 验证群号逻辑 (在 Conversation 内部)
async def check_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip().upper()
    
    # 条件：前四个字是“报备编号”，则直接跳出并回复报备信息
    if user_input.startswith("报备编号"):
        await send_baobei_info(update)
        return ConversationHandler.END

    # 正常的名单比对
    if user_input in VALID_GROUPS:
        res = f"✅ 查询结果：【{user_input}】\n该群为已查证的公群或专群，可放心交易。"
    else:
        res = f"❌ 查询结果：【{user_input}】\n未查证到该编号！注意⚠️是假群，请勿交易。"

    await update.message.reply_text(res, reply_markup=main_reply_markup)
    return ConversationHandler.END

# 普通消息和菜单按钮处理
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text: return

    # 条件：前四个字是“报备编号”
    if text.startswith("报备编号"):
        await send_baobei_info(update)
    elif text == "人工客服":
        await update.message.reply_text("正在为您分配人工客服，请稍后...")
    elif text == "资源对接":
        await update.message.reply_text("请联系官方频道了解详细资源信息。")
    elif text == "纠纷仲裁":
        await update.message.reply_text("请提供您的交易证明和群编号，稍后会有专人处理。")

# --- 3. 主程序入口 ---
def main():
    if not TOKEN:
        print("错误: 请在环境变量中配置 BOT_TOKEN")
        return
        
    app = Application.builder().token(TOKEN).build()
    
    # 验群流程处理器
    verify_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^自助验群$'), start_verify)],
        states={
            WAITING_GROUP_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_group_id)],
        },
        fallbacks=[CommandHandler("start", start)],
        allow_reentry=True # 允许在状态中重新点击菜单
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(verify_handler)
    # 处理所有其他文字消息
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("🚀 最终整理版机器人已启动，不依赖数据库，纯净运行中...")
    app.run_polling()

if __name__ == "__main__":
    main()
