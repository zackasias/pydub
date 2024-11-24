from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from pydub import AudioSegment
import os

def upscale_to_flac(input_file, output_file, sample_rate=96000, channels=2):
    """
    Upscale an audio file to FLAC format with enhanced sample rate and channels.
    """
    try:
        # Load the audio file
        audio = AudioSegment.from_file(input_file)

        # Resample audio
        audio = audio.set_frame_rate(sample_rate).set_channels(channels)

        # Export as FLAC
        audio.export(output_file, format="flac")
        return True
    except Exception as e:
        print(f"Error during processing: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the bot starts."""
    await update.message.reply_text(
        "Welcome! Send me an audio file, and I will upscale it to FLAC format."
    )

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle audio files sent to the bot."""
    audio_file = update.message.audio or update.message.voice

    if not audio_file:
        await update.message.reply_text("Please send a valid audio file.")
        return

    # Download the audio file
    file = await audio_file.get_file()
    file_path = await file.download_to_drive()
    output_file = file_path.split('.')[0] + "_upscaled.flac"

    # Upscale the audio file
    await update.message.reply_text("Processing your audio file...")
    success = upscale_to_flac(file_path, output_file)

    if success:
        # Send the upscaled audio file back
        with open(output_file, "rb") as f:
            await update.message.reply_audio(f, caption="Here is your upscaled FLAC file!")

        # Clean up files
        os.remove(file_path)
        os.remove(output_file)
    else:
        await update.message.reply_text("Sorry, something went wrong during processing.")

def main():
    """Start the Telegram bot."""
    # Replace 'YOUR_TOKEN' with your bot token
    TOKEN = "5707293090:AAHGLlHSx101F8T1DQYdcb9_MkRAjyCbt70"

    application = ApplicationBuilder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.AUDIO | filters.VOICE, handle_audio))

    # Start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    # Ensure ffmpeg is installed
    if not os.system("ffmpeg -version") == 0:
        print("Error: FFmpeg is not installed or not in PATH. Please install FFmpeg.")
        exit(1)

    main()
