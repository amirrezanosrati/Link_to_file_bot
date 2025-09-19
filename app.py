from flask import Flask, request, jsonify
import requests
import os
import logging

app = Flask(__name__)
TOKEN = os.environ.get('TELEGRAM_TOKEN')
logging.basicConfig(level=logging.INFO)

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
        
        # پردازش پیام‌های تلگرام
        data = request.get_json()
        
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            
            # پاسخ فوری
            requests.post(
                f'https://api.telegram.org/bot{TOKEN}/sendMessage',
                json={
                    'chat_id': chat_id, 
                    'text': '✅ ربات فعال شد! لطفا فایل ارسال کنید.',
                    'parse_mode': 'HTML'
                },
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
