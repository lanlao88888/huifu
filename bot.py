import redis
import logging
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# --- 1. 环境配置 ---
TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID_VAL = os.getenv("ADMIN_ID", "7934724103").strip()
REDIS_URL = os.getenv("REDIS_URL", "")

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- 2. 数据库连接加固 (全局定义) ---
r = None

def get_redis():
    global r
    if r is None:
        try:
            # 增加 socket_timeout 防止 Railway 网络波动卡死
            r = redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=5)
            r.ping()
            logging.info("✅ Redis 连接成功")
        except Exception as e:
            logging.error(f"❌ Redis 连接失败: {e}")
            r = None
    return r

# --- 3. 增强版数据库函数 ---
def save_group_to_db(group_id):
    conn = get_redis()
    if conn:
        # 统一转为大写字符串并去除空格，防止 88 和 88 匹配失败
        clean_id = str(group_id).strip().upper()
        return conn.sadd("valid_groups_set", clean_id)
    return False

def is_group_valid(group_id):
    conn = get_redis()
    if conn:
        clean_id = str(group_id).strip().upper()
        return conn.sismember("valid_groups_set", clean_id)
    return False

# --- 4. 业务逻辑处理 ---
WAITING_GROUP_ID = 1
MAIN_MENU = [['人工客服', '资源对接'], ['自助验群', '纠纷仲裁']]
main_reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("您好，欢迎来到微担保服务中心 😊", reply_markup=main_reply_markup)

async def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # 权限双重锁定：数字 ID 或 用户名
    is_admin = (str(user.id) == ADMIN_ID_VAL) or (user.username == "danbao_11")
    
    if not is_admin:
        await update.message.reply_text(f"❌ 无权限。您的ID是: {user.id}")
        return

    if not context.args:
        await update.message.reply_text("💡 用法：`/add 编号` (例如: /add 88)")
        return

    new_id = context.args[0].strip().upper()
    if save_group_to_db(new_id):
        await update.message.reply_text(f"✅ 录入成功：{new_id}")
    else:
        await update.message.reply_text(f"ℹ️ 编号 {new_id} 已在库中。")

async def start_verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 请输入您需要验证的群编号：")
    return WAITING_GROUP_ID

async def check_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip().upper()
    
    if is_group_valid(user_input):
        res = f"✅ 查询结果：【{user_input}】\n该群为已验证公群，请放心交易。"
    else:
        res = f"❌ 查询结果：【{user_input}】\n未查证到该编号！注意假群。"

    await update.message.reply_text(res, reply_markup=main_reply_markup)
    return ConversationHandler.END

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
