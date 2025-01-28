import os  # Module for interacting with the operating system
import telebot  # Library for working with the Telegram Bot API
import yt_dlp as youtube_dl  # Library for downloading videos from YouTube
import subprocess  # Module for executing system commands

# Create a bot object with the token for accessing the Telegram Bot API
bot = telebot.TeleBot("API")

# Dictionary to track active video downloads
active_downloads = {}

# Handler for the /start command, which sends a welcome message
@bot.message_handler(commands=['start'])
def shoot(message):
    bot.send_message(message.chat.id, "Give me your YouTube link Zhanym:3")

# Handler for all other messages
@bot.message_handler()
def run(message):
    # Check if the message contains a YouTube link
    if "youtube.com" not in message.text and "youtu.be" not in message.text:
        # If not, send an error message
        bot.send_message(message.chat.id, "This is not a valid YouTube link.")

    bot.send_message(message.chat.id, "Please wait...")

    try:
        video_info = youtube_dl.YoutubeDL().extract_info(
            url=message.text, download=False
        )
        filename = f"{video_info['title']}.mp3"
        options = {
            'format': 'bestaudio/best',
            'keepvideo': False,
            'outtmpl': filename,
        }

        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([video_info['webpage_url']])

        active_downloads[message.chat.id] = filename

        print(f"Download complete... {filename}")
        bot.send_audio(message.chat.id, audio=open(filename, 'rb'))
        os.remove(filename)
    except Exception as e:
        bot.send_message(message.chat.id, "Sorry, there was an error. Please try again later.")
        print(f"Error: {e}")

@bot.message_handler(commands=['rewind', 'forward'])
def handle_seek(message):
    if message.chat.id not in active_downloads:
        bot.send_message(message.chat.id, "No active audio file to seek.")
        return

    command = message.text.strip().lower()
    filename = active_downloads.get(message.chat.id)


    seek_time = 30  
    if command == '/rewind':
        bot.send_message(message.chat.id, "Rewinding the track...")

        output_filename = "rewind_output.mp3"
        subprocess.call(['ffmpeg', '-ss', f"00:00:{seek_time}", '-i', filename, '-c', 'copy', output_filename])

        bot.send_audio(message.chat.id, audio=open(output_filename, 'rb'))

        os.remove(output_filename)

    elif command == '/forward':
        bot.send_message(message.chat.id, "Skipping ahead in the track...")

        output_filename = "forward_output.mp3"
        subprocess.call(['ffmpeg', '-ss', f"00:00:{seek_time}", '-i', filename, '-c', 'copy', output_filename])

        bot.send_audio(message.chat.id, audio=open(output_filename, 'rb'))
        os.remove(output_filename)

bot.polling()
