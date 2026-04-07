@echo off
echo ========================================
echo YouTube Downloader .exe 빌드
echo ========================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo https://www.python.org/downloads/ 에서 Python을 설치하세요.
    pause
    exit /b 1
)

echo [1/2] 필요한 패키지 설치 중...
pip install yt-dlp pyinstaller
echo.

echo [2/2] .exe 파일 생성 중...
pyinstaller --onefile --windowed --name "YouTubeDownloader" youtube_downloader.py
echo.

if exist "dist\YouTubeDownloader.exe" (
    echo ========================================
    echo 빌드 완료!
    echo 결과물: dist\YouTubeDownloader.exe
    echo ========================================
    echo.
    echo 참고: ffmpeg.exe도 dist 폴더에 복사해야 고화질/MP3 변환이 작동합니다.
) else (
    echo [오류] 빌드에 실패했습니다.
)
pause
