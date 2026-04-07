import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import yt_dlp
import os
import sys
import subprocess

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube 영상 다운로더")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.is_downloading = False
        self.create_widgets()
        self.check_ffmpeg()

    def _get_bundle_dir(self):
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        else:
            return os.path.dirname(os.path.abspath(__file__))

    def check_ffmpeg(self):
        bundle_dir = self._get_bundle_dir()
        local_ffmpeg = os.path.join(bundle_dir, "ffmpeg.exe")
        if os.path.exists(local_ffmpeg):
            self.log(f"FFmpeg 감지: {local_ffmpeg}")
        else:
            try:
                subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.log("FFmpeg 감지됨 (시스템 PATH)")
            except FileNotFoundError:
                self.log("경고: FFmpeg가 없습니다. 고화질/MP3 변환이 실패할 수 있습니다.")
                self.log("ffmpeg.exe를 이 프로그램과 같은 폴더에 넣어주세요.")

    def get_ffmpeg_path(self):
        bundle_dir = self._get_bundle_dir()
        local_ffmpeg = os.path.join(bundle_dir, "ffmpeg.exe")
        if os.path.exists(local_ffmpeg):
            return local_ffmpeg
        return None

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        url_frame = ttk.LabelFrame(main_frame, text="YouTube URL (한 줄에 하나씩, 재생목록 URL 지원)", padding="10")
        url_frame.pack(fill=tk.X, pady=(0, 10))

        self.url_text = scrolledtext.ScrolledText(url_frame, height=5, font=("맑은 고딕", 10))
        self.url_text.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(0, 5))
        ttk.Button(url_frame, text="붙여넣기", command=self.paste_url).pack(side=tk.RIGHT)

        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(path_frame, text="저장 경로:").pack(anchor=tk.W)
        path_inner = ttk.Frame(path_frame)
        path_inner.pack(fill=tk.X, pady=(5, 0))
        self.path_entry = ttk.Entry(path_inner, font=("맑은 고딕", 10))
        self.path_entry.insert(0, self.download_path)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(path_inner, text="찾아보기", command=self.browse_path).pack(side=tk.RIGHT)

        option_frame = ttk.LabelFrame(main_frame, text="다운로드 옵션", padding="10")
        option_frame.pack(fill=tk.X, pady=(0, 10))

        quality_inner = ttk.Frame(option_frame)
        quality_inner.pack(fill=tk.X)
        ttk.Label(quality_inner, text="화질:").pack(side=tk.LEFT, padx=(0, 10))

        self.quality_var = tk.StringVar(value="best")
        for text, value in [("최고 화질", "best"), ("1080p", "bestvideo[height<=1080]"), ("720p", "bestvideo[height<=720]"), ("360p", "bestvideo[height<=360]"), ("오디오만", "audio")]:
            ttk.Radiobutton(quality_inner, text=text, variable=self.quality_var, value=value).pack(side=tk.LEFT, padx=3)

        format_inner = ttk.Frame(option_frame)
        format_inner.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(format_inner, text="포맷:").pack(side=tk.LEFT, padx=(0, 10))
        self.format_var = tk.StringVar(value="mp4")
        for text, value in [("MP4", "mp4"), ("WEBM", "webm"), ("MP3", "mp3")]:
            ttk.Radiobutton(format_inner, text=text, variable=self.format_var, value=value).pack(side=tk.LEFT, padx=3)

        progress_frame = ttk.LabelFrame(main_frame, text="진행 상황", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        self.progress = ttk.Progressbar(progress_frame, mode="determinate")
        self.progress.pack(fill=tk.X, pady=(0, 5))
        self.status_label = ttk.Label(progress_frame, text="대기 중", font=("맑은 고딕", 10))
        self.status_label.pack(anchor=tk.W)

        self.log_text = scrolledtext.ScrolledText(progress_frame, height=6, state=tk.DISABLED, font=("맑은 고딕", 8))
        self.log_text.pack(fill=tk.X, pady=(5, 0))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        self.download_btn = ttk.Button(button_frame, text="다운로드", command=self.start_download)
        self.download_btn.pack(side=tk.LEFT, padx=5, ipadx=20, ipady=5)
        ttk.Button(button_frame, text="폴더 열기", command=self.open_folder).pack(side=tk.LEFT, padx=5, ipadx=20, ipady=5)

    def paste_url(self):
        try:
            self.url_text.insert(tk.END, self.root.clipboard_get().strip() + "\n")
        except tk.TclError:
            pass

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def open_folder(self):
        if os.path.exists(self.path_entry.get()):
            os.startfile(self.path_entry.get())

    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def progress_hook(self, d):
        if d["status"] == "downloading":
            p = d.get("_percent_str", "?").strip()
            s = d.get("_speed_str", "?").strip()
            self.root.after(0, lambda: self.status_label.config(text=f"다운로드 중: {p} ({s})"))

    def download(self):
        urls = [line.strip() for line in self.url_text.get("1.0", tk.END).strip().split("\n") if line.strip()]
        if not urls:
            self.root.after(0, lambda: messagebox.showwarning("경고", "URL을 입력하세요."))
            return

        save_path = self.path_entry.get()
        quality = self.quality_var.get()
        fmt = self.format_var.get()
        os.makedirs(save_path, exist_ok=True)

        self.root.after(0, lambda: self.download_btn.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.log_text.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.log_text.delete("1.0", tk.END))
        self.root.after(0, lambda: self.log_text.config(state=tk.DISABLED))

        ffmpeg_loc = self.get_ffmpeg_path()

        for i, url in enumerate(urls, 1):
            self.log(f"[{i}/{len(urls)}] 시작: {url}")

            try:
                ydl_opts = {
                    "outtmpl": os.path.join(save_path, "%(title)s.%(ext)s"),
                    "progress_hooks": [self.progress_hook],
                }

                if ffmpeg_loc:
                    ydl_opts["ffmpeg_location"] = ffmpeg_loc

                if quality == "audio" or fmt == "mp3":
                    ydl_opts["format"] = "bestaudio/best"
                    ydl_opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
                else:
                    ydl_opts["format"] = f"{quality}+bestaudio/best" if quality != "best" else "best"
                    ydl_opts["merge_output_format"] = fmt

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                self.log(f"[{i}/{len(urls)}] 완료!")

            except Exception as e:
                self.log(f"[{i}/{len(urls)}] 오류: {str(e)}")

        self.root.after(0, lambda: self.status_label.config(text="모두 완료!"))
        self.root.after(0, lambda: messagebox.showinfo("완료", f"{len(urls)}개 URL 처리가 완료되었습니다."))
        self.root.after(0, lambda: self.download_btn.config(state=tk.NORMAL))

    def start_download(self):
        threading.Thread(target=self.download, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    YouTubeDownloader(root)
    root.mainloop()
