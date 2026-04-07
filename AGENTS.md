# YouTube Downloader Project

## 개요
YouTube 영상 URL을 입력하여 영상을 다운로드하는 Windows 데스크톱 애플리케이션입니다.
Python, Tkinter, yt-dlp를 사용하며, PyInstaller를 통해 단일 실행 파일(.exe)로 배포됩니다.

## 파일 구조
- `youtube_downloader.py`: 메인 애플리케이션 소스 코드 (GUI 및 다운로드 로직)
- `make_exe.py`: 자동 빌드 스크립트 (필요 패키지 설치, FFmpeg 다운로드, PyInstaller 실행)
- `setup.iss`: Inno Setup 설치 프로그램 스크립트 (선택 사항)
- `dist/`: 빌드된 실행 파일이 저장되는 폴더

## 주요 기능
- **URL 입력**: YouTube 영상 URL 붙여넣기
- **화질 선택**: 최고 화질, 1080p, 720p, 360p, 오디오만
- **포맷 선택**: MP4, WEBM, MP3
- **진행 상황**: 실시간 다운로드 진행률 및 속도 표시
- **FFmpeg 자동 포함**: 빌드 시 FFmpeg를 자동으로 다운로드하여 exe에 포함

## 빌드 방법
1. 명령 프롬프트(cmd)를 엽니다.
2. 현재 폴더(`D:\youtube`)로 이동합니다.
3. 다음 명령어를 실행합니다:
   ```cmd
   python make_exe.py
   ```
4. 빌드가 완료되면 `dist` 폴더에 `YouTubeDownloader.exe`가 생성됩니다.

## 배포
- `dist\YouTubeDownloader.exe` 파일 하나만 다른 사용자에게 전달하면 됩니다.
- 사용자는 Python이나 FFmpeg를 별도로 설치할 필요가 없습니다.

## 기술 스택
- **Language**: Python 3.x
- **GUI**: Tkinter
- **Download**: yt-dlp
- **Packaging**: PyInstaller
- **Media Processing**: FFmpeg (자동 포함)

## 주의사항
- 저작권이 있는 영상은 개인 소장 목적으로만 사용하세요.
- YouTube 이용약관을 준수하세요.
