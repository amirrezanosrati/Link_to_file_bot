from flask import Flask, request, jsonify
import requests
import os
import logging

app = Flask(__name__)
TOKEN = os.environ.get('TELEGRAM_TOKEN')
logging.basicConfig(level=logging.INFO)

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

@app.route('/')
def home():
    return "🤖 Bot Server is Running! Use /webhook for Telegram"

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    try:
        if request.method == 'GET':
            return jsonify({
                "status": "active",
                "message": "Webhook endpoint is ready for Telegram messages",
                "bot_token_configured": bool(TOKEN)
            })

        # 📌 داده ورودی تلگرام
        data = request.get_json()

        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]

            if "document" in message or "video" in message:
                file_info = message.get("document") or message.get("video")
                file_id = file_info["file_id"]

                # 📌 گرفتن مسیر فایل
                file_path_resp = requests.get(f"{BASE_URL}/getFile?file_id={file_id}", timeout=10).json()
                file_path = file_path_resp["result"]["file_path"]
                download_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"

                # 📌 پیام اولیه
                progress_msg = requests.post(
                    f"{BASE_URL}/sendMessage",
                    json={"chat_id": chat_id, "text": "⬇️ دانلود شروع شد..."},
                    timeout=10
                ).json()
                msg_id = progress_msg["result"]["message_id"]

                # 📥 دانلود با Progress
                local_filename = file_path.split("/")[-1]
                r = requests.get(download_url, stream=True, timeout=60)
                total = int(r.headers.get("content-length", 0))
                downloaded = 0

                with open(local_filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 256):  # 256KB
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            percent = int(downloaded * 100 / total)

                            # 📌 هر 10% یک بار آپدیت کن
                            if percent % 10 == 0:
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

                # 📌 پیام نهایی
                requests.post(
                    f"{BASE_URL}/editMessageText",
                    json={
                        "chat_id": chat_id,
                        "message_id": msg_id,
                        "text": f"✅ دانلود کامل شد!\n📂 فایل ذخیره شد: {local_filename}"
                    },
                    timeout=10
                )

            else:
                # وقتی پیام فایل نبود
                requests.post(
                    f"{BASE_URL}/sendMessage",
                    json={"chat_id": chat_id, "text": "✅ ربات فعال شد! لطفا فایل ارسال کنید."},
                    timeout=5
                )

        return jsonify({"status": "success"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/test')
def test():
    return jsonify({
        "status": "active",
        "server": "Render",
        "webhook_ready": True
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
