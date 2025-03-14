import os
import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from dotenv import load_dotenv

# 🔹 Load Environment Variables
load_dotenv()

# 🔹 Load API Keys
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")  # Replace with your Spotify Client ID
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")  # Replace with your Spotify Client Secret
TELEGRAM_BOT_TOKEN = os.environ.get("LISTEN2PLAY_BOT_TOKEN")  # Replace with your Telegram Bot Token

# 🔹 Logging Setup
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# 🔹 Validate Environment Variables
if not TELEGRAM_BOT_TOKEN:
    logging.error("❌ Telegram Bot Token is missing. Please check your .env file.")
    exit(1)

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
        response.raise_for_status()  # Raise an error for bad status codes
        logging.info("🔑 Spotify token fetched successfully.")
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get Spotify token: {e}")
        return None

# 🔹 Function to Search for a Song on Spotify
def search_song(song_name):
    token = get_spotify_token()
    if not token:
        return "❌ Failed to authenticate with Spotify."

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
            url = track["external_urls"]["spotify"]
            return f"🎵 {name} by {artist}\n🔗 {url}"
        else:
            return "❌ No song found!"
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to search for song: {e}")
        return "❌ Failed to search for the song. Please try again later."

# 🔹 Telegram Command: /song <song name>
async def song_command(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("❌ Please provide a song name! Example: /song Believer")
        return

    song_name = " ".join(context.args)
    logging.info(f"Searching for song: {song_name}")
    result = search_song(song_name)
    await update.message.reply_text(result)

# 🔹 Start Telegram Bot
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("song", song_command))

    logging.info("🚀 Listen2PlayBot is running...")
    app.run_polling()

# 🔹 Run the bot
if __name__ == "_main_":
    main()  # ✅ Correctly called at the top level