import os
import re
import logging
from pyrogram import Client, filters
from yt_dlp import YoutubeDL

# Logging setup
logging.basicConfig(level=logging.INFO)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN", "7878501468:AAHwa1_Lq-PgHlMvf80VuEfrOcMNzuP3CSY")
API_ID = int(os.getenv("API_ID", "28982243"))
API_HASH = os.getenv("API_HASH", "c4cba546fd17ca535b0880a0c3ab7e9b")

# Create downloads directory if it doesn't exist
os.makedirs("downloads", exist_ok=True)

# Bot client
app = Client("kr_premium_downloader",
             bot_token=BOT_TOKEN,
             api_id=API_ID,
             api_hash=API_HASH)


# Start command
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "**🌟 স্বাগতম KR Premium Downloader এ!**\n\n"
        "**সাপোর্টেড প্ল্যাটফর্ম:**\n"
        "🎥 YouTube\n"
        "📘 Facebook\n\n"
        "**কিভাবে ব্যবহার করবেন:**\n"
        "📹 যেকোনো সাপোর্টেড লিংক পাঠান এবং ভিডিও ডাউনলোড করুন\n\n"
        "**উদাহরণ:**\n"
        "• `https://youtu.be/abc123`\n"
        "• `https://facebook.com/video123`",
        quote=True)


def is_supported_url(url):
    """Check if URL is from supported platforms"""
    url_lower = url.lower()
    supported_domains = [
        'youtube.com', 'youtu.be', 'youtube-nocookie.com',
        'facebook.com', 'fb.watch', 'm.facebook.com'
    ]
    return any(domain in url_lower for domain in supported_domains)


def get_downloader_config():
    """Get YouTube/Facebook optimized downloader configuration"""
    return {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'best[filesize<50M]/best',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
        },
        'sleep_interval': 1,
        'no_warnings': True,
        'ignoreerrors': False,
    }


# Link handler
@app.on_message(filters.text & ~filters.command(["start"]))
async def video_downloader(client, message):
    """Handle video downloads from text messages"""
    url = message.text.strip()
    await download_content(client, message, url)


async def download_content(client, message, url):
    """Common download function for both video and audio"""
    # Check if it's a valid URL
    if not re.match(r'https?://', url):
        await message.reply_text("⚠️ দয়া করে সঠিক লিংক পাঠান!")
        return

    # Check if URL is from supported platforms
    if not is_supported_url(url):
        await message.reply_text(
            "❌ এই প্ল্যাটফর্ম সাপোর্ট করা হয় না!\n\n"
            "**সাপোর্টেড প্ল্যাটফর্ম:**\n"
            "🎥 YouTube (youtube.com, youtu.be)\n"
            "📘 Facebook (facebook.com, fb.watch)\n\n"
            "দয়া করে YouTube বা Facebook লিংক ব্যবহার করুন।")
        return

    await message.reply_text("🔄 ভিডিও ডাউনলোড শুরু হচ্ছে, দয়া করে অপেক্ষা করুন...")

    try:
        # Detect platform for user feedback
        url_lower = url.lower()
        if 'youtube' in url_lower or 'youtu.be' in url_lower:
            platform = "YouTube"
            await message.reply_text("🎥 YouTube ভিডিও ডিটেক্ট হয়েছে...")
        elif 'facebook' in url_lower or 'fb.watch' in url_lower:
            platform = "Facebook"
            await message.reply_text("📘 Facebook ভিডিও ডিটেক্ট হয়েছে...")

        # Download with optimized settings
        ydl_opts = get_downloader_config()

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB

            await message.reply_video(
                file_path, 
                caption=f"✅ 🎥 ভিডিও ডাউনলোড সম্পন্ন! ({file_size:.1f}MB)\n\n"
                       f"📱 KR Premium Downloader"
            )

            # Clean up
            os.remove(file_path)
        else:
            await message.reply_text("❌ ফাইল পাওয়া যায়নি!")

    except Exception as e:
        error_msg = str(e).lower()

        if "rate" in error_msg or "limit" in error_msg or "429" in error_msg:
            await message.reply_text(
                "❌ সার্ভার ব্যস্ত আছে!\n\n"
                "**সমাধান:**\n"
                "⏰ 5-10 মিনিট অপেক্ষা করুন এবং আবার চেষ্টা করুন")
        elif "private" in error_msg or "unavailable" in error_msg:
            await message.reply_text(
                "❌ কনটেন্টটি প্রাইভেট বা উপলব্ধ নেই!\n\n"
                "**সমাধান:**\n"
                "🔓 পাবলিক কনটেন্টের লিংক ব্যবহার করুন")
        elif "age" in error_msg or "sign" in error_msg:
            await message.reply_text(
                "❌ এই কনটেন্টটি বয়স সীমাবদ্ধতা বা সাইন-ইন প্রয়োজন!\n\n"
                "**সমাধান:**\n"
                "👶 সর্বসাধারণের জন্য উপলব্ধ কনটেন্ট চেষ্টা করুন")
        else:
            await message.reply_text(
                f"❌ ডাউনলোড ব্যর্থ হয়েছে!\n\n"
                "**সুপারিশ:**\n"
                "🎯 YouTube লিংক সবচেয়ে নির্ভরযোগ্য\n"
                "📱 কনটেন্টটি পাবলিক কি না চেক করুন")


# Run bot
app.run()