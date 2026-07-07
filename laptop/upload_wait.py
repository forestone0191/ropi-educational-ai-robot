from pathlib import Path
import requests

ROPI_SERVER_URL = "http://192.168.219.127:8000"

BASE_DIR = Path(__file__).resolve().parent
WAIT_FILE = BASE_DIR / "wait.mp3"


def main():
    if not WAIT_FILE.exists():
        print("wait.mp3가 없습니다. 먼저 make_wait_voice.py를 실행하세요.")
        return

    response = requests.get(ROPI_SERVER_URL + "/status", timeout=5)
    print("서버 확인:", response.status_code, response.text)

    with open(WAIT_FILE, "rb") as f:
        files = {"file": ("wait.mp3", f, "audio/mpeg")}
        response = requests.post(ROPI_SERVER_URL + "/upload_wait", files=files, timeout=60)

    print("업로드:", response.status_code, response.text)

    response = requests.get(ROPI_SERVER_URL + "/say/wait", timeout=20)
    print("재생 테스트:", response.status_code, response.text)


if __name__ == "__main__":
    main()
