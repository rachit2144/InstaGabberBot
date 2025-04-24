import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = "7606801933:AAG0mseXzK1XjWM9-UMZJm-A1JdJ6IZU86c"  # Replace with your actual bot token

user_urls = {}

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to *InstaGabberBot*!\n\n"
        "📥 Send any Instagram Reel link, and choose format: MP4 🎥 or MP3 🎵.",
        parse_mode="Markdown"
    )

# URL handler
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    chat_id = update.message.chat_id
    user_urls[chat_id] = url

    keyboard = [
        [
            InlineKeyboardButton("🎥 MP4", callback_data="mp4"),
            InlineKeyboardButton("🎵 MP3", callback_data="mp3"),
        ]
    ]
    await update.message.reply_text("Select format:", reply_markup=InlineKeyboardMarkup(keyboard))

# Download handler
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    choice = query.data
    chat_id = query.message.chat_id
    url = user_urls.get(chat_id)

    if not url:
        await query.edit_message_text("❗ URL not found. Please send it again.")
        return

    await query.edit_message_text(f"📥 Downloading as {choice.upper()}... Please wait...")

    try:
        ydl_opts = {
            'quiet': True,
            'outtmpl': '%(title).30s.%(ext)s'
        }

        if choice == 'mp3':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            ydl_opts['format'] = 'mp4'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if choice == "mp3":
                filename = os.path.splitext(filename)[0] + ".mp3"

        with open(filename, 'rb') as f:
            if choice == "mp4":
                await query.message.reply_video(f, caption="✅ Here's your MP4 video!")
            else:
                await query.message.reply_audio(f, caption="✅ Here's your MP3 audio!")

        os.remove(filename)

        # Send "Download Another" button
        again_keyboard = [[InlineKeyboardButton("🔁 Download Another", callback_data="restart")]]
        await query.message.reply_text("Want to download another reel?", reply_markup=InlineKeyboardMarkup(again_keyboard))

    except Exception as e:
        print("❌ Error:", e)
        await query.message.reply_text("⚠️ Download failed. Please try again with a valid link.")

# Restart handler
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("📥 Send another Instagram Reel link.")

# Main function
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    app.add_handler(CallbackQueryHandler(button, pattern="^(mp4|mp3)$"))
    app.add_handler(CallbackQueryHandler(restart, pattern="^restart$"))

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
