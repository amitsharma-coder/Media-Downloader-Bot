from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp
import os
import re
import asyncio

# ✅ Option 1: Hardcoded token (if you're not using environment variables)
BOT_TOKEN = os.getenv("8129065922:AAGR6fx4tUzqVw6P4Et4ARr5vD88Gbg-J8U")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a media link (photo/video/audio), and I’ll download it!")

async def is_valid_url(text):
    pattern = re.compile(r'(https?://[^\s]+)')
    return re.match(pattern, text)

async def animate_progress(message, context):
    animation = ["⏳", "⌛", "🔄", "⚙️", "📥", "📤"]
    for _ in range(6):
        try:
            await context.bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=message.message_id,
                text=f"Downloading... {animation[_ % len(animation)]}"
            )
        except:
            pass
        await asyncio.sleep(1)

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not await is_valid_url(url):
        await asyncio.sleep(2)
        await update.message.reply_text("Please send a valid media link.")
        return

    message = await update.message.reply_text("Preparing to download... ⏳")
    animation_task = asyncio.create_task(animate_progress(message, context))

    try:
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'quiet': True,
        }

        os.makedirs('downloads', exist_ok=True)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        caption_text = f"🎬 {info.get('title', 'Video')}\n👤 {info.get('uploader', '')}"

        await animation_task
        await context.bot.edit_message_text(
            chat_id=message.chat_id,
            message_id=message.message_id,
            text="Download complete! ✅ Sending file..."
        )

        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                if filename.endswith('.mp4'):
                    await update.message.reply_video(f, caption=caption_text[:1024])
                elif filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    await update.message.reply_photo(f, caption=caption_text[:1024])
                else:
                    await update.message.reply_document(f, caption=caption_text[:1024])
            os.remove(filename)
        else:
            await update.message.reply_text("Download done but file not found!")

    except Exception as e:
        await animation_task
        await update.message.reply_text(f"Error: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download))

    # Corrected Webhook URL and Path setup
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url=f"https://api.render.com/deploy/srv-d0c7jcp5pdvs73dbe180?key=xTYb4wt7pyg",  # Replace with actual server URL
        url_path="your_custom_path"  # Optional custom path
    )
