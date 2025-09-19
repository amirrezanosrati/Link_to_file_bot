import requests

# اطلاعات ربات
TOKEN = "7897337548:AAGudjNDkUM5pUWx93mdc6kFBrSqusuj_NA"
# آدرس Render شما - مهم!
RENDER_URL = "https://your-bot-name.onrender.com/webhook"

print("🔧 در حال تنظیم Webhook...")

# حذف وبhook قبلی
delete_response = requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
print("🗑️ حذف وبhook قبلی:", delete_response.json())

# تنظیم وبhook جدید
set_response = requests.get(
    f"https://api.telegram.org/bot{TOKEN}/setWebhook",
    params={
        "url": RENDER_URL,
        "drop_pending_updates": True,
        "allowed_updates": ["message", "document", "video"]
    }
)

print("✅ تنظیم وبhook جدید:", set_response.json())

# بررسی وضعیت
info_response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo")
print("📋 وضعیت وبhook:", info_response.json())
