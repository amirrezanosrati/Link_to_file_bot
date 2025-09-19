from flask import Flask, request, jsonify, send_from_directory
import requests
import os
import logging

app = Flask(__name__)
TOKEN = os.environ.get('TELEGRAM_TOKEN')
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# مسیر ذخیره فایل‌ها
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    return "🤖 Bot Server is Running! Use /webhook for Telegram"

# 📂 مسیر عمومی برای دانلود فایل‌ها
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    try:
        if request.method == 'GET':
            return jsonify({
                "status": "active",
                "message": "Webhook endpoint is ready for Telegram messages",
                "bot_token_configured": bool(TOKEN)
            })

        data = request.get_json()

        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]

            if "document" in message or "video" in message:
                file_info = message.get("document") or message.get("video")
                file_id = file_info["file_id"]
                file_name = file_info.get("file_name", "file.dat")

                # گرفتن لینک فایل از تلگرام
                file_path_resp = requests.get(f"{BASE_URL}/getFile?file_id={file_id}", timeout=10).json()
                if not file_path_resp.get("ok"):
                    requests.post(f"{BASE_URL}/sendMessage", json={
                        "chat_id": chat_id,
                        "text": "❌ خطا در گرفتن فایل از تلگرام!"
                    })
                    return jsonify({"error": "getFile failed"})

                file_path = file_path_resp["result"]["file_path"]
                download_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"

                # پیام اولیه
                progress_msg = requests.post(
                    f"{BASE_URL}/sendMessage",
                    json={"chat_id": chat_id, "text": "⬇️ دانلود شروع شد..."},
                    timeout=10
                ).json()
                msg_id = progress_msg["result"]["message_id"]

                # دانلود با progress
                local_path = os.path.join(UPLOAD_FOLDER, file_name)
                r = requests.get(download_url, stream=True, timeout=60)
                total = int(r.headers.get("content-length", 0))
                downloaded = 0

                with open(local_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 256):  # 256KB
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total > 0:
                                percent = int(downloaded * 100 / total)
                                if percent % 10 == 0:  # هر 10% آپدیت
                                    try:
                                        requests.post(
                                            f"{BASE_URL}/editMessageText",
                                            json={
                                                "chat_id": chat_id,
                                                "message_id": msg_id,
                                                "text": f"⬇️ در حال دانلود...\n{percent}% تکمیل شد"
                                            },
                                            timeout=5
                                        )
                                    except:
                                        pass

                # پیام نهایی + لینک عمومی
                public_url = f"{request.url_root}uploads/{file_name}"
                requests.post(
                    f"{BASE_URL}/editMessageText",
                    json={
                        "chat_id": chat_id,
                        "message_id": msg_id,
                        "text": f"✅ دانلود کامل شد!\n📂 [دانلود فایل]({public_url})",
                        "parse_mode": "Markdown"
                    },
                    timeout=10
                )

            else:
                requests.post(
                    f"{BASE_URL}/sendMessage",
                    json={"chat_id": chat_id, "text": "✅ لطفا یک فایل یا ویدیو ارسال کنید."},
                    timeout=5
                )

        return jsonify({"status": "success"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
