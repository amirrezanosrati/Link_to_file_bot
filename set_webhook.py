# set_webhook.py
import requests

TOKEN = "7897337548:AAGudjNDkUM5pUWx93mdc6kFBrSqusuj_NA"
RENDER_URL = "https://personalfiletolink007bot.onrender.com/webhook"

print("🔄 Resetting webhook...")

# حذف وبhook قبلی
response = requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
print("Delete result:", response.json())

# تنظیم مجدد وبhook
response = requests.get(
    f"https://api.telegram.org/bot{TOKEN}/setWebhook",
    params={
        "url": RENDER_URL,
        "drop_pending_updates": True,
        "allowed_updates": ["message", "document", "video", "photo"]
    }
)

print("Set webhook result:", response.json())

# بررسی نهایی
response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo")
print("Final webhook status:", response.json())
