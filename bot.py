import logging
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# --- 1. 配置区域 ---
TOKEN = os.getenv("BOT_TOKEN", "")
# 你的 ID，确保和环境变量一致，用于校验所有者权限
ADMIN_ID_VAL = os.getenv("ADMIN_ID", "7934724103").strip()

# 初始名单（代码重启后会恢复到这个初始状态）
VALID_GROUPS = [
   "66", "88", "90", "91", "92", "116", "117", "118", "100","130", "131", 
    "132", "133", "134", "135", "136", "137", "138", "139", 
    "006","166","167", "168", "333", "A222", "B188"
]

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- 2. 核心功能函数 ---
WAITING_GROUP_ID = 1
MAIN_MENU = [['人工客服', '资源对接'], ['自助验群', '纠纷仲裁']]
main_reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)

# 报备信息模板
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

# --- 新增：所有者添加编号功能 ---
async def add_new_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # 权限校验：只允许 ADMIN_ID 或特定用户名
    if str(user.id) != ADMIN_ID_VAL and user.username != "danbao_11":
        await update.message.reply_text("❌ 您没有权限添加编号。")
        return

    if not context.args:
        await update.message.reply_text("💡 用法：`/add 编号` (例如: `/add 999`)")
        return

    new_id = context.args[0].strip().upper()
    if new_id in VALID_GROUPS:
        await update.message.reply_text(f"ℹ️ 编号 【{new_id}】 已经在名单中了。")
    else:
        VALID_GROUPS.append(new_id)
        await update.message.reply_text(f"✅ 成功添加编号：【{new_id}】\n当前共有 {len(VALID_GROUPS)} 个验证编号。")

# 触发自助验群
async def start_verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 请输入您需要验证的群编号：")
    return WAITING_GROUP_ID

# 验证群号逻辑
async def check_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip().upper()
    
    # 优先拦截报备编号
    if user_input.startswith("报备编号"):
        await send_baobei_info(update)
        return ConversationHandler.END

    if user_input in VALID_GROUPS:
        res = f"✅ 查询结果：【{user_input}】\n该群为已查证的公群或专群，可放心交易。"
    else:
        res = f"❌ 查询结果：【{user_input}】\n未查证到该编号！注意⚠️是假群，请勿交易。"

    await update.message.reply_text(res, reply_markup=main_reply_markup)
    return ConversationHandler.END

# 处理菜单按钮和关键词
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text: return

    if text.startswith("报备编号"):
        await send_baobei_info(update)
    elif text == "人工客服":
        await update.message.reply_text("正在为您分配人工客服...")
    # ...其他菜单逻辑

def main():
    if not TOKEN: return
    app = Application.builder().token(TOKEN).build()
    
    verify_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^自助验群$'), start_verify)],
        states={
            WAITING_GROUP_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_group_id)],
        },
        fallbacks=[CommandHandler("start", start)],
        allow_reentry=True 
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_new_group)) # 注册添加指令
    app.add_handler(verify_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    app.run_polling()

if __name__ == "__main__":
    main()
