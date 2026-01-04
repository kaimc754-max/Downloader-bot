import telebot
import requests

BOT_TOKEN = "5992875466:AAGU1C42aXsrnCnSoO9n5omqqbCdMdnitYI"
BASE = "https://www.xoffline.com"
API = f"{BASE}/callDownloaderApi"

API_TOKEN = "3c409435f781890e402cdf7312aa47f2a7e23594f5615ce524f8e711bc69acc5"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")


def fetch_download(video_url: str):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
        "Accept": "*/*",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": BASE + "/",
    })

    session.get(BASE + "/", timeout=20)

    csrf = session.cookies.get("x-csrf-token")
    sid = session.cookies.get("connect.sid")

    if not csrf or not sid:
        raise RuntimeError("Failed to get session tokens")


    headers = {
        "Content-Type": "application/json",
        "Origin": BASE,
        "X-CSRF-Token": csrf,
    }

    payload = {
        "apiToken": API_TOKEN,
        "apiValue": video_url,
    }

    r = session.post(API, headers=headers, json=payload, timeout=30)
    r.raise_for_status()

    data = r.json()["data"][0]

    final_url = data["url"]
    if final_url.startswith("https://href.li/?"):
        final_url = final_url.replace("https://href.li/?", "", 1)

    return {
        "title": data["title"],
        "thumbnail": data["thumbnail"],
        "quality": data["quality"],
        "url": final_url,
    }

@bot.message_handler(commands=["start"])
def start(msg):
    bot.reply_to(
        msg,
        "<b>🎬 Corn Downloader Bot</b>\n\n"
        "Send me a <b>video URL</b> and I’ll give you the direct MP4 link.\n\n"
        "<i>Powered by Basic Coders</i>"
    )

@bot.message_handler(func=lambda m: m.text and m.text.startswith("http"))
def handle_url(msg):
    wait = bot.reply_to(msg, "⏳ Processing your link...")

    try:
        info = fetch_download(msg.text.strip())

        caption = (
            f"<b>{info['title']}</b>\n\n"
            f"🎞 Quality: <b>{info['quality']}</b>\n\n"
            f"⬇️ <a href='{info['url']}'>Download MP4</a>"
        )

        bot.delete_message(msg.chat.id, wait.message_id)
        bot.send_photo(
            msg.chat.id,
            info["thumbnail"],
            caption=caption
        )

    except Exception as e:
        bot.edit_message_text(
            "❌ Failed to fetch download link.\nTry again later.",
            msg.chat.id,
            wait.message_id
        )

print("🤖 Bot running...")
bot.infinity_polling()
