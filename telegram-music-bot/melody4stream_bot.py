import os
import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from yt_dlp import YoutubeDL
from telethon import TelegramClient

# 🔹 Load API Keys
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")  # Your Spotify Client ID
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")  # Your Spotify Client Secret
TELEGRAM_BOT_TOKEN = os.environ.get("MELODY4STREAM_BOT_TOKEN")  # Your Telegram Bot Token
TELEGRAM_API_ID = int(os.environ.get("TELEGRAM_API_ID"))  # Your Telegram API ID
TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH")  # Your Telegram API Hash

# 🔹 Logging Setup
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# 🔹 Initialize Telethon Client
telethon_client = TelegramClient("melody4stream", TELEGRAM_API_ID, TELEGRAM_API_HASH)

# 🔹 Initialize PyTgCalls
call = PyTgCalls(telethon_client)

# 🔹 Initialize Telegram Bot
app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# 🔹 Function to Get Spotify Access Token
def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get Spotify token: {e}")
        return None

# 🔹 Function to Search Song on Spotify
def search_song(song_name):
    token = get_spotify_token()
    if not token:
        return None, None, None

    url = f"https://api.spotify.com/v1/search?q={song_name}&type=track&limit=1"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if "tracks" in data and data["tracks"]["items"]:
            track = data["tracks"]["items"][0]
            name = track["name"]
            artist = track["artists"][0]["name"]
            spotify_url = track["external_urls"]["spotify"]
            return name, artist, spotify_url
        else:
            return None, None, None
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to search for song: {e}")
        return None, None, None

# 🔹 Function to Get YouTube Audio URL
def get_youtube_audio(song_name):
    ydl_opts = {"format": "bestaudio", "noplaylist": True}
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{song_name}", download=False)
            return info["entries"][0]["url"] if info["entries"] else None
    except Exception as e:
        logging.error(f"Failed to fetch YouTube audio: {e}")
        return None

# 🔹 Telegram Command: /play <song name>
async def play_command(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("❌ Please provide a song name! Example: /play Believer")
        return

    song_name = " ".join(context.args)
    name, artist, spotify_url = search_song(song_name)

    if not name:
        await update.message.reply_text("❌ No song found!")
        return

    youtube_url = get_youtube_audio(f"{name} by {artist}")

    if not youtube_url:
        await update.message.reply_text("❌ Couldn't find an audio source for this song.")
        return

    chat_id = update.message.chat.id
    try:
        await call.join_group_call(chat_id, AudioPiped(youtube_url))
        await update.message.reply_text(f"🎵 Playing *{name}* by *{artist}*\n🔗 [Listen on Spotify]({spotify_url})", parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Failed to join voice chat: {e}")
        await update.message.reply_text("❌ Failed to join voice chat. Please try again.")

# 🔹 Telegram Command: /stop
async def stop_command(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    try:
        await call.leave_group_call(chat_id)
        await update.message.reply_text("🛑 Stopped playing music!")
    except Exception as e:
        logging.error(f"Failed to leave voice chat: {e}")
        await update.message.reply_text("❌ Failed to stop playback. Please try again.")

# 🔹 Start Telegram Bot
def main():
    app.add_handler(CommandHandler("play", play_command))
    app.add_handler(CommandHandler("stop", stop_command))

    logging.info("🚀 Melody4StreamBot is running...")
    telethon_client.start()
    call.start()
    app.run_polling()

# 🔹 Run the bot
if __name__ == "_main_":
    main()