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
    user = update.effective_user
    user_id = user.id
    username = user.username # 获取用户名，例如 danbao_11
    
    # 打印调试信息到 Railway Logs
    print(f"DEBUG: 尝试操作 - ID: {user_id}, 用户名: {username}, 设定管理员ID: {ADMIN_ID}")

    # --- 双重检查逻辑 ---
    # 只要 [ID 匹配] 或者 [用户名匹配]，就给权限
    is_admin = (user_id == ADMIN_ID) or (username == "danbao_11")

    if not is_admin:
        await update.message.reply_text(f"❌ 您没有权限。您的ID是: {user_id}, 用户名是: @{username}")
        return

    # 权限通过，执行添加逻辑
    if not context.args:
        await update.message.reply_text("💡 用法：`/add 编号` (例如: /add A112)")
        return

    new_id = context.args[0].strip()
    if save_group_to_db(new_id):
        await update.message.reply_text(f"✅ 认证成功！管理员 @{username}\n已成功收录编号：{new_id}")
    else:
        await update.message.reply_text(f"ℹ️ 编号 {new_id} 已经存在于数据库中。")

async def start_verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("请输入您需要验证的群编号，如：123、A112。")
    return WAITING_GROUP_ID

async def check_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # .strip() 非常重要，它能去掉用户不小心多打的空格或换行符
    user_input = update.message.text.strip()
    
    # 调试信息：看看机器人到底收到了什么
    print(f"DEBUG: 用户正在查询编号: '{user_input}'")

    # 这里的 is_group_valid 会去 Redis 数据库里查找
    if is_group_valid(user_input):
        res = (
            f"✅ 查询结果：【{user_input}】\n"
            f"该群为已查证的公群或专群，可放心交易。"
        )
    else:
        res = (
            f"❌ 查询结果：【{user_input}】\n"
            f"未查证到该编号！注意⚠️是假群，请勿交易。"
        )

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
