
import logging
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# --- 配置区 ---
TOKEN = ""
ADMIN_ID =  7934724103 # 【重要】替换为你的Telegram数字ID
DB_FILE = "groups_db.txt"  # 存储群编号的文件

# 启用日志
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


# --- 数据持久化函数 ---
def load_groups():
    if not os.path.exists(DB_FILE):
        return set()
    with open(DB_FILE, "r", encoding="utf-8") as f:
        # 读取每一行并去掉换行符和空格
        return set(line.strip() for line in f if line.strip())


def save_group(group_id):
    groups = load_groups()
    if group_id not in groups:
        with open(DB_FILE, "a", encoding="utf-8") as f:
            f.write(f"{group_id}\n")
        return True
    return False


# 初始化加载
VALID_GROUPS = load_groups()

# --- 状态与菜单定义 ---
WAITING_GROUP_ID = 1
MAIN_MENU = [['人工客服', '资源对接'], ['自助验群', '纠纷仲裁']]
main_reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)


# --- 管理员功能：添加群组 ---
async def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 鉴权：只有管理员能操作
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ 您没有权限执行此操作。")
        return

    # 检查参数 (用法: /add A112)
    if not context.args:
        await update.message.reply_text("💡 用法错误。请输入：`/add 编号`\n例如：`/add A112`", parse_mode="Markdown")
        return

    new_id = context.args[0].strip()
    if save_group(new_id):
        global VALID_GROUPS
        VALID_GROUPS = load_groups()  # 重新载入内存
        await update.message.reply_text(f"✅ 已成功收录群组编号：{new_id}")
    else:
        await update.message.reply_text(f"ℹ️ 编号 {new_id} 已经存在于数据库中。")


# --- 基础功能逻辑 ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "您好，欢迎来到微担保服务中心，请点击下方对应的业务板块选择您要办理的业务😊",
        reply_markup=main_reply_markup
    )


async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # 关键词监控
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

    # 普通菜单回复
    responses = {
        "人工客服": "正在分配人工客服，请耐心等待...",
        "资源对接": "请详细说明您需要对接的板块...",
        "纠纷仲裁": "请先描述您纠纷的内容及群号..."
    }
    if text in responses:
        await update.message.reply_text(responses[text])


# --- 专项：自助验群流程 ---
async def start_verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("请输入您需要验证的群编号，如：123、A112。")
    return WAITING_GROUP_ID


async def check_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    # 每次查询时直接对比内存中的 VALID_GROUPS
    if user_input in VALID_GROUPS:
        res = f"✅ 查询结果：【{user_input}】\n该群为已查证的公群或专群，可放心交易。"
    else:
        res = f"❌ 查询结果：【{user_input}】\n未查证到该编号！注意⚠是假群，请勿交易。"

    await update.message.reply_text(res, reply_markup=main_reply_markup)
    return ConversationHandler.END


# --- 主程序 ---
def main():
    app = Application.builder().token(TOKEN).build()

    # 对话处理器
    verify_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^自助验群$'), start_verify)],
        states={
            WAITING_GROUP_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_group_id)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # 注册处理器
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_group))  # 管理员添加命令
    app.add_handler(verify_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))

    print("机器人已启动。管理员可通过 /add 增加群编号。")
    app.run_polling()


if __name__ == "__main__":
    main()
