import redis
import logging
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# --- 1. 严格配置处理 ---
TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID_VAL = os.getenv("ADMIN_ID", "7934724103").strip()
REDIS_URL = os.getenv("REDIS_URL", "")

# 启用日志
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- 2. 数据库连接 (使用全局变量并增加重连机制) ---
def get_redis_connection():
    try:
        connection = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=10)
        connection.ping()
        return connection
    except Exception as e:
        logging.error(f"Redis连接失败: {e}")
        return None

# 初始化连接
r = get_redis_connection()

# --- 3. 增强版数据库函数 ---
def save_group_to_db(group_id):
    global r
    if not r: r = get_redis_connection() # 自动重连
    if r:
        return r.sadd("valid_groups_set", str(group_id).strip())
    return False

def is_group_valid(group_id):
    global r
    if not r: r = get_redis_connection() # 自动重连
    if r:
        return r.sismember("valid_groups_set", str(group_id).strip())
    return False

# --- 4. 业务逻辑 ---
WAITING_GROUP_ID = 1
MAIN_MENU = [['人工客服', '资源对接'], ['自助验群', '纠纷仲裁']]
main_reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("您好，欢迎来到微担保服务中心 😊", reply_markup=main_reply_markup)

async def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # 权限判断：同时对比 ID 和 用户名
    is_admin = (str(user.id) == ADMIN_ID_VAL) or (user.username == "danbao_11")
    
    if not is_admin:
        await update.message.reply_text(f"❌ 无权限。您的ID: {user.id}")
        return

    if not context.args:
        await update.message.reply_text("💡 用法：`/add 编号`")
        return

    new_id = context.args[0].strip()
    if save_group_to_db(new_id):
        await update.message.reply_text(f"✅ 成功收录编号：{new_id}")
    else:
        await update.message.reply_text(f"ℹ️ 编号 {new_id} 已在库中。")

async def start_verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("请输入需要验证的群编号：")
    return WAITING_GROUP_ID

async def check_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    if is_group_valid(user_input):
        res = f"✅ 查询结果：【{user_input}】\n该群为已查证公群，请放心交易。"
    else:
        res = f"❌ 查询结果：【{user_input}】\n未查证到该编号！注意假群。"
    
    await update.message.reply_text(res, reply_markup=main_reply_markup)
    return ConversationHandler.END

# --- 5. 主函数 ---
def main():
    if not TOKEN: return
    app = Application.builder().token(TOKEN).build()
    
    verify_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^自助验群$'), start_verify)],
        states={WAITING_GROUP_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_group_id)]},
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_group))
    app.add_handler(verify_handler)
    
    app.run_polling()

if __name__ == "__main__":
    main()
