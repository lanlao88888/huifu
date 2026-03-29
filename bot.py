import redis
import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# --- 1. 配置 ---
TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID_STR = os.getenv("ADMIN_ID", "7934724103")
REDIS_URL = os.getenv("REDIS_URL", "")

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- 2. 数据库连接 (必须全局化且增加重连) ---
def get_redis_conn():
    try:
        # 增加 decode_responses=True 确保拿到的是字符串
        conn = redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=5)
        conn.ping()
        return conn
    except Exception as e:
        logging.error(f"Redis连接失败: {e}")
        return None

# --- 3. 修正后的数据库操作函数 ---
def save_group_to_db(group_id):
    r_conn = get_redis_conn() # 每次操作重新获取连接
    if r_conn:
        # 强制清除空格并转大写，确保存取一致
        clean_id = str(group_id).strip().upper()
        return r_conn.sadd("valid_groups_set", clean_id)
    return False

def is_group_valid(group_id):
    r_conn = get_redis_conn()
    if r_conn:
        clean_id = str(group_id).strip().upper()
        return r_conn.sismember("valid_groups_set", clean_id)
    return False

# --- 4. 业务逻辑 ---
WAITING_GROUP_ID = 1
MAIN_MENU = [['人工客服', '资源对接'], ['自助验群', '纠纷仲裁']]
main_reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)

async def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # 权限双保障：ID 匹配或用户名匹配
    is_admin = (str(user.id) == ADMIN_ID_STR.strip()) or (user.username == "danbao_11")
    
    if not is_admin:
        await update.message.reply_text(f"❌ 无权限。您的ID是: {user.id}")
        return

    if not context.args:
        await update.message.reply_text("💡 用法：`/add 编号`")
        return

    new_id = context.args[0].strip().upper()
    if save_group_to_db(new_id):
        await update.message.reply_text(f"✅ 录入成功：{new_id}")
    else:
        # 如果显示已存在，说明 Redis 里已经有这个 clean_id 了
        await update.message.reply_text(f"ℹ️ 编号 {new_id} 已在库中。")

async def check_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip().upper()
    
    # 这里调用修正后的 is_group_valid，不会再报 NameError
    if is_group_valid(user_input):
        res = f"✅ 查询结果：【{user_input}】\n该群为已验证公群，请放心交易。"
    else:
        res = f"❌ 查询结果：【{user_input}】\n未查证到该编号！注意假群。"

    await update.message.reply_text(res, reply_markup=main_reply_markup)
    return ConversationHandler.END

# ... 其他 handle_all_messages 等函数保持不变 ...
# --- 5. 启动入口 ---
def main():
    if not TOKEN:
        print("错误: 未配置 BOT_TOKEN")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    verify_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^自助验群$'), start_verify)],
        states={
            WAITING_GROUP_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_group_id)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_group))
    app.add_handler(verify_handler)
    
    print("🚀 机器人正在 Railway 启动...")
    app.run_polling()

if __name__ == "__main__":
    main()
