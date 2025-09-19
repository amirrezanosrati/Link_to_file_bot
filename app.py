from flask import Flask, request
import requests
import os
import logging

app = Flask(__name__)

# تنظیمات
TOKEN = os.environ.get('TELEGRAM_TOKEN')
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    return "🤖 Telegram Bot is Running on Render!"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            
            if 'text' in message:
                text = message['text']
                if text == '/start':
                    send_message(chat_id, "🎉 **ربات فعال شد!**\n\nارسال فایل را شروع کنید...")
                else:
                    send_message(chat_id, "📨 پیام شما دریافت شد!")
            
            elif 'document' in message:
                file = message['document']
                send_message(chat_id, f"📄 فایل دریافت شد!\nنام: {file['file_name']}\nحجم: {file['file_size']} بایت")
            
            elif 'video' in message:
                video = message['video']
                send_message(chat_id, f"🎥 ویدیو دریافت شد!\nمدت: {video['duration']} ثانیه")
    
    except Exception as e:
        logging.error(f"Error: {e}")
    
    return 'OK'

def send_message(chat_id, text):
    """ارسال پیام به کاربر"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        logging.error(f"Error sending message: {e}")

# این خط برای Render ضروری است
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
