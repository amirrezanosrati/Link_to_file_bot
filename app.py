# app.py - کد اصلاح شده
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
        # برای تست GET
        if request.method == 'GET':
            return jsonify({
                "status": "active", 
                "message": "Webhook endpoint is ready",
                "token_set": bool(TOKEN)
            })
        
        # برای POST requests از تلگرام
        data = request.get_json()
        logging.info(f"📨 Received data from Telegram")
        
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            
            # پاسخ فوری به کاربر
            response = requests.post(
                f'https://api.telegram.org/bot{TOKEN}/sendMessage',
                json={
                    'chat_id': chat_id, 
                    'text': '✅ ربات فعال شد! فایل ارسال کنید.',
                    'parse_mode': 'HTML'
                },
                timeout=10
            )
            
            logging.info(f"📤 Sent response to user: {response.status_code}")
            
        return jsonify({"status": "success"})
        
    except Exception as e:
        logging.error(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/test')
def test():
    return jsonify({
        "status": "active", 
        "token_configured": bool(TOKEN),
        "endpoints": {
            "home": "/",
            "webhook": "/webhook", 
            "test": "/test"
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
