from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import sys
import subprocess
import threading
import time
import json

app = Flask(__name__)

download_status = {
    "progress": 0,
    "status": "idle",
    "message": "대기 중",
    "log": [],
    "speed": "",
    "eta": "",
}

def get_bundle_dir():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.abspath(__file__))

def get_ffmpeg_path():
    bundle_dir = get_bundle_dir()
    local_ffmpeg = os.path.join(bundle_dir, "ffmpeg.exe")
    if os.path.exists(local_ffmpeg):
        return local_ffmpeg
    return None

def progress_hook(d):
    if d["status"] == "downloading":
        p = d.get("_percent_str", "?").strip()
        s = d.get("_speed_str", "?").strip()
        eta = d.get("_eta_str", "?").strip()
        try:
            pct = float(p.replace("%", ""))
        except:
            pct = 0
        download_status["progress"] = pct
        download_status["speed"] = s
        download_status["eta"] = eta
        download_status["message"] = f"다운로드 중: {p} ({s})"
    elif d["status"] == "finished":
        download_status["status"] = "processing"
        download_status["message"] = "변환 중..."
        download_status["progress"] = 100

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/download", methods=["POST"])
def download():
    data = request.json
    urls = [line.strip() for line in data.get("urls", "").strip().split("\n") if line.strip()]
    save_path = data.get("save_path", os.path.join(os.path.expanduser("~"), "Downloads"))
    quality = data.get("quality", "best")
    fmt = data.get("format", "mp4")

    if not urls:
        return jsonify({"error": "URL을 입력하세요."}), 400

    os.makedirs(save_path, exist_ok=True)

    download_status["progress"] = 0
    download_status["status"] = "downloading"
    download_status["message"] = "시작 중..."
    download_status["log"] = []
    download_status["speed"] = ""
    download_status["eta"] = ""

    ffmpeg_loc = get_ffmpeg_path()

    def run_download():
        for i, url in enumerate(urls, 1):
            download_status["log"].append(f"[{i}/{len(urls)}] 시작: {url}")
            try:
                ydl_opts = {
                    "outtmpl": os.path.join(save_path, "%(title)s.%(ext)s"),
                    "progress_hooks": [progress_hook],
                }
                if ffmpeg_loc:
                    ydl_opts["ffmpeg_location"] = ffmpeg_loc

                if quality == "audio" or fmt == "mp3":
                    ydl_opts["format"] = "bestaudio/best"
                    ydl_opts["postprocessors"] = [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192"
                    }]
                else:
                    ydl_opts["format"] = f"{quality}+bestaudio/best" if quality != "best" else "best"
                    ydl_opts["merge_output_format"] = fmt

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                download_status["log"].append(f"[{i}/{len(urls)}] 완료!")
            except Exception as e:
                download_status["log"].append(f"[{i}/{len(urls)}] 오류: {str(e)}")

        download_status["status"] = "completed"
        download_status["message"] = "모두 완료!"
        download_status["progress"] = 100

    thread = threading.Thread(target=run_download, daemon=True)
    thread.start()

    return jsonify({"message": "다운로드 시작됨"})

@app.route("/api/status")
def status():
    return jsonify(download_status)

@app.route("/api/reset", methods=["POST"])
def reset():
    download_status["progress"] = 0
    download_status["status"] = "idle"
    download_status["message"] = "대기 중"
    download_status["log"] = []
    download_status["speed"] = ""
    download_status["eta"] = ""
    return jsonify({"message": "초기화됨"})

@app.route("/api/paths")
def get_paths():
    return jsonify({
        "default_path": os.path.join(os.path.expanduser("~"), "Downloads"),
        "current_path": request.args.get("path", os.path.join(os.path.expanduser("~"), "Downloads"))
    })

def open_browser(port):
    import webbrowser
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe"),
    ]
    chrome_path = None
    for p in chrome_paths:
        if os.path.exists(p):
            chrome_path = p
            break
    if chrome_path:
        webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(chrome_path))
        webbrowser.get("chrome").open(f"http://127.0.0.1:{port}")
    else:
        webbrowser.open(f"http://127.0.0.1:{port}")

if __name__ == "__main__":
    port = 5000
    threading.Timer(1.5, open_browser, args=[port]).start()
    app.run(debug=False, host="127.0.0.1", port=port)
