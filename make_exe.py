import subprocess
import sys
import os
import urllib.request
import zipfile
import tempfile
import shutil

def download_ffmpeg(dest_path):
    print("[A] FFmpeg 다운로드 중... (시간이 걸릴 수 있습니다)")
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "ffmpeg.zip")
    
    try:
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(temp_dir)
        
        for root, dirs, files in os.walk(temp_dir):
            for f in files:
                if f == "ffmpeg.exe":
                    src = os.path.join(root, f)
                    shutil.copy2(src, dest_path)
                    print("FFmpeg 준비 완료.")
                    return True
        return False
    except Exception as e:
        print(f"FFmpeg 다운로드 실패: {e}")
        return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    print("=" * 50)
    print("YouTube Downloader 웹앱 .exe 빌드 (Flask + FFmpeg)")
    print("=" * 50)
    print()

    print("[1/4] 필요한 패키지 설치 중...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp", "pyinstaller", "flask"])
    print()

    ffmpeg_file = "ffmpeg.exe"
    if not os.path.exists(ffmpeg_file):
        if not download_ffmpeg(ffmpeg_file):
            print("FFmpeg 준비에 실패했습니다. 빌드를 중단합니다.")
            input("Enter를 누르면 종료됩니다...")
            return
    else:
        print("[2/4] 기존 FFmpeg 사용")
    
    print()
    print("[3/4] templates 폴더 확인 중...")
    if not os.path.isdir("templates"):
        print("templates 폴더가 없습니다!")
        input("Enter를 누르면 종료됩니다...")
        return
    print("templates 폴더 확인 완료.")
    
    print()
    print("[4/4] .exe 파일 생성 중 (Flask + templates + FFmpeg 포함)...")
    subprocess.check_call([
        sys.executable, "-m", "PyInstaller",
        "--onefile", "--windowed",
        "--clean",
        "--add-data", f"{ffmpeg_file};.",
        "--add-data", "templates;templates",
        "--hidden-import", "flask",
        "--hidden-import", "jinja2",
        "--name", "YouTubeDownloader",
        "app.py"
    ])
    print()

    exe_path = os.path.join("dist", "YouTubeDownloader.exe")
    if os.path.exists(exe_path):
        print("=" * 50)
        print("빌드 완료!")
        print(f"결과물: {exe_path}")
        print("=" * 50)
        print()
        print("이제 이 파일 하나만 더블클릭하면 브라우저가 자동으로 열립니다!")
    else:
        print("[오류] 빌드에 실패했습니다.")

    input("\nEnter를 누르면 종료됩니다...")

if __name__ == "__main__":
    main()
