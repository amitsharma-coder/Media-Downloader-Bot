import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)
import yt_dlp

TOKEN = "8129065922:AAGR6fx4tUzqVw6P4Et4ARr5vD88Gbg-J8U"  # <-- Yaha apna bot token paste karo

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a video or image link to download!")

# Emoji Animation
async def animate_progress(message, context):
    animation = ["⏳", "⌛", "🔄", "⚙", "📥", "📤"]
    for i in range(6):
        try:
            await context.bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=message.message_id,
                text=f"Downloading... {animation[i % len(animation)]}"
            )
            await asyncio.sleep(1)
        except:
            break

# Download Handler
async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    # Validate URL
    if not url.startswith("http"):
        await asyncio.sleep(2)
        await update.message.reply_text("Please send a valid link.")
        return

    msg = await update.message.reply_text("Preparing to download... ⏳")
    animation_task = asyncio.create_task(animate_progress(msg, context))

    try:
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await animation_task
        await context.bot.edit_message_text(
            chat_id=msg.chat_id,
            message_id=msg.message_id,
            text="Download complete! ✅ Sending..."
        )

        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                if filename.endswith(".mp4"):
                    await update.message.reply_video(f)
                else:
                    await update.message.reply_document(f)
            os.remove(filename)
        else:
            await update.message.reply_text("File not found after download.")

    except Exception as e:
        await animation_task
        await update.message.reply_text(f"Error: {e}")

    # Auto delete original "Downloading..." message
    try:
        await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)
    except:
        pass

# Main
if _name_ == '_main_':
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_handler))
    print("Bot running...")
    app.run_polling()
