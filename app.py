from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio
from collections import deque
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS = [int(x) for x in os.getenv("ADMINS", "").split(",") if x.strip()]
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

MESSAGE_COUNT = 0
LAST_MESSAGES = deque(maxlen=10)

def is_admin(chat_id: int) -> bool:
    return chat_id in ADMINS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("خوش اومدی به ⚫ Rawline — بی‌هویت بفرست، فقط vibe.")

async def send_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_chat.id):
        return await update.effective_message.reply_text("فقط ادمین‌ها می‌تونن از این دستور استفاده کنن.")
    msg = " ".join(context.args).strip()
    if not msg:
        return await update.effective_message.reply_text("متن خالیه. مثال: /send یه پیام برای کانال")
    await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
    await update.effective_message.reply_text("✅ به کانال ارسال شد.")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_chat.id):
        return await update.effective_message.reply_text("دسترسی نداری.")
    report = [f"📊 مجموع پیام‌های ناشناس: {MESSAGE_COUNT}"]
    if LAST_MESSAGES:
        for i, m in enumerate(LAST_MESSAGES, 1):
            report.append(f"{i}. {m}")
    else:
        report.append("هنوز پیام ناشناس ثبت نشده.")
    await update.effective_message.reply_text("\n".join(report))

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.effective_chat.id):
        return
    global MESSAGE_COUNT
    MESSAGE_COUNT += 1
    text = (update.effective_message.text or "").strip()
    if not text:
        return
    LAST_MESSAGES.append(text)
    notify = f"📥 پیام ناشناس:\n{text}"
    await asyncio.gather(*[
        context.bot.send_message(chat_id=admin_id, text=notify)
        for admin_id in ADMINS
    ])
    await update.effective_message.reply_text("✅ پیام ناشناس برای ادمین‌ها ارسال شد.")

def main():
    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send", send_cmd))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
