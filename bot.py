import os
import asyncio
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ✅ BOT_TOKEN Koyeb Environment থেকে আসবে
BOT_TOKEN = os.getenv("BOT_TOKEN")

CHANNEL_1 = "1002023435387"
CHANNEL_2 = "1002872277979"

POST_INTERVAL_SECONDS = 10 * 3600  # Default: 10 hours

async def copy_posts():
    bot = Bot(BOT_TOKEN)
    try:
        updates = await bot.get_updates(timeout=10)
        for update in updates:
            if update.channel_post and str(update.channel_post.chat_id) == CHANNEL_1:
                post = update.channel_post
                try:
                    if post.text:
                        await bot.send_message(chat_id=CHANNEL_2, text=post.text)
                    elif post.photo:
                        await bot.send_photo(
                            chat_id=CHANNEL_2,
                            photo=post.photo[-1].file_id,
                            caption=post.caption
                        )
                except Exception as e:
                    print(f"Error sending post: {e}")
    except Exception as e:
        print(f"Error fetching updates: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running! Automated posting is active.")

def parse_time_string(time_str: str) -> int:
    """Convert strings like '10s', '5m', '2h' to seconds."""
    try:
        unit = time_str[-1].lower()
        value = int(time_str[:-1])
        if unit == 's':
            return value
        elif unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 3600
    except:
        return None
    return None

async def setinterval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global POST_INTERVAL_SECONDS, job, scheduler
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /setinterval <time> (e.g., 10s, 5m, 2h)")
        return
    
    seconds = parse_time_string(context.args[0])
    if seconds is None or seconds <= 0:
        await update.message.reply_text("Invalid format! Use 10s, 5m, 2h etc.")
        return
    
    POST_INTERVAL_SECONDS = seconds
    
    if job:
        scheduler.remove_job(job.id)
    
    job = scheduler.add_job(copy_posts, 'interval', seconds=POST_INTERVAL_SECONDS)
    await update.message.reply_text(f"⏰ Interval updated! Posts will be sent every {context.args[0]}.")

# ===== Main =====
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("setinterval", setinterval))

loop = asyncio.get_event_loop()
scheduler = AsyncIOScheduler(event_loop=loop)
job = scheduler.add_job(copy_posts, 'interval', seconds=POST_INTERVAL_SECONDS)
scheduler.start()

print("🚀 Bot is running safely on Koyeb...")

loop.create_task(app.run_polling())
loop.run_forever()
