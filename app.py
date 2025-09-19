from flask import Flask, request, jsonify
import requests
import os
import logging
import tempfile
import threading
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)
TOKEN = "7897337548:AAGudjNDkUM5pUWx93mdc6kFBrSqusuj_NA"
logging.basicConfig(level=logging.INFO)

# دایرکتوری موقت برای آپلود
UPLOAD_FOLDER = tempfile.mkdtemp()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# راه اندازی Ngrok
def setup_ngrok():
    try:
        # دانلود Ngrok
        os.system("wget -q https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz -O ngrok.tgz")
        os.system("tar -xzf ngrok.tgz && chmod +x ngrok")
        
        # راه اندازی tunnel
        os.system("./ngrok authtoken YOUR_NGROK_AUTH_TOKEN")  # توکن Ngrok خود را قرار دهید
        os.system("./ngrok http 5000 > ngrok.log 2>&1 &")
        time.sleep(5)
        
        # دریافت آدرس Ngrok
        try:
            response = requests.get("http://localhost:4040/api/tunnels")
            ngrok_url = response.json()['tunnels'][0]['public_url']
            return ngrok_url
        except:
            return "https://example.com"  # fallback
    except:
        return "https://example.com"

NGROK_URL = setup_ngrok()

@app.route('/')
def home():
    return f"🤖 Bot Server with Ngrok! Ngrok URL: {NGROK_URL}"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            
            # بررسی نوع محتوا
            if 'document' in message:
                file_info = message['document']
                file_type = "document"
                file_name = file_info.get('file_name', 'file')
                
            elif 'video' in message:
                file_info = message['video']
                file_type = "video"
                file_name = f"video_{file_info['file_id']}.mp4"
                
            elif 'photo' in message:
                file_info = message['photo'][-1]  # بزرگترین سایز
                file_type = "photo" 
                file_name = f"photo_{file_info['file_id']}.jpg"
                
            else:
                requests.post(
                    f'https://api.telegram.org/bot{TOKEN}/sendMessage',
                    json={'chat_id': chat_id, 'text': '⚠️ لطفا یک فایل ارسال کنید'}
                )
                return 'OK'
            
            # اطلاع رسانی شروع پردازش
            requests.post(
                f'https://api.telegram.org/bot{TOKEN}/sendMessage',
                json={'chat_id': chat_id, 'text': '📥 فایل دریافت شد! در حال آپلود...'}
            )
            
            # دانلود فایل از تلگرام
            file_response = requests.get(f'https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_info["file_id"]}')
            file_path = file_response.json()['result']['file_path']
            
            download_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'
            file_data = requests.get(download_url)
            
            # ذخیره فایل موقت
            safe_filename = secure_filename(file_name)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
            
            with open(file_path, 'wb') as f:
                f.write(file_data.content)
            
            # ایجاد لینک دانلود با Ngrok
            download_link = f"{NGROK_URL}/download/{safe_filename}"
            
            # ارسال لینک به کاربر
            requests.post(
                f'https://api.telegram.org/bot{TOKEN}/sendMessage',
                json={
                    'chat_id': chat_id,
                    'text': f'✅ فایل شما آماده است!\n\n📁 نام: {file_name}\n📦 حجم: {len(file_data.content)} بایت\n🔗 لینک دانلود: {download_link}\n⏰ لینک 1 ساعت معتبر است',
                    'parse_mode': 'HTML'
                }
            )
            
        return 'OK'
        
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        safe_filename = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        
        if os.path.exists(file_path):
            return requests.get(f"http://localhost:4040/api/tunnels").content
        else:
            return "File not found", 404
            
    except Exception as e:
        return str(e), 500

@app.route('/status')
def status():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify({
        "status": "active",
        "ngrok_url": NGROK_URL,
        "files_available": files,
        "upload_folder": app.config['UPLOAD_FOLDER']
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
