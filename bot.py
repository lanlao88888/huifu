import redis
import logging
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# --- 1. 配置与数据库连接 ---
# 直接从系统环境获取，并增加默认值防止报错
TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID_STR = os.getenv("ADMIN_ID", "0")
# 这里的处理是为了确保万一环境变量读取有空格也能转成数字
try:
    ADMIN_ID = int(ADMIN_ID_STR.strip())
except:
    ADMIN_ID = 0

REDIS_URL = os.getenv("REDIS_URL")

# 启用日志
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 初始化 Redis 变量
r = None 
if REDIS_URL:
    try:
        r = redis.from_url(REDIS_URL, decode_responses=True)
        logging.info("成功连接到 Redis 数据库")
    except Exception as e:
        logging.error(f"Redis 连接失败: {e}")
else:
    logging.error("错误: 未在环境变量中找到 REDIS_URL")

# --- 2. 数据库操作函数 ---

def save_group_to_db(group_id):
    if r:
        return r.sadd("valid_groups_set", group_id)
    return False

def is_group_valid(group_id):
    if r:
        return r.sismember("valid_groups_set", group_id)
    return False

# --- 3. 菜单与状态定义 ---
WAITING_GROUP_ID = 1
MAIN_MENU = [['人工客服', '资源对接'], ['自助验群', '纠纷仲裁']]
main_reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)

# --- 4. 业务处理逻辑 ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "您好，欢迎来到微担保服务中心，请点击下方对应的业务板块选择您要办理 of 业务😊",
        reply_markup=main_reply_markup
    )

async def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # 在日志中输出，方便排查
    print(f"DEBUG: 用户 {user_id} 尝试添加，系统设定的管理员是 {ADMIN_ID}")

    if user_id != ADMIN_ID:
        # 增加反馈信息，如果你看到 ID 还是不一致，就说明环境变量没生效
        await update.message.reply_text(f"❌ 您没有权限。您的ID是: {user_id}")
        return

    if not context.args:
        await update.message.reply_text("💡 用法：`/add 编号`")
        return

    new_id = context.args[0].strip()
    if save_group_to_db(new_id):
        await update.message.reply_text(f"✅ 已成功收录编号：{new_id}")
    else:
        await update.message.reply_text(f"ℹ️ 编号 {new_id} 已经存在。")

async def start_verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("请输入您需要验证的群编号，如：123、A112。")
    return WAITING_GROUP_ID

async def check_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    if is_group_valid(user_input):
        res = f"✅ 查询结果：【{user_input}】\n该群为已查证的公群或专群，可放心交易。"
    else:
        res = f"❌ 查询结果：【{user_input}】\n未查证到该编号！注意⚠是假群，请勿交易。"
    await update.message.reply_text(res, reply_markup=main_reply_markup)
    return ConversationHandler.END

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text: return

    if text.startswith("报备编号"):
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

    responses = {
        "人工客服": "正在分配人工客服，请耐心等待...",
        "资源对接": "请详细说明您需要对接的板块...",
        "纠纷仲裁": "请先描述您纠纷的内容及群号..."
    }
    if text in responses:
        await update.message.reply_text(responses[text])

def main():
    if not TOKEN:
        print("错误: 未检测到 BOT_TOKEN")
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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))

    print("机器人已启动...")
    app.run_polling()

if __name__ == "__main__":
    main()
