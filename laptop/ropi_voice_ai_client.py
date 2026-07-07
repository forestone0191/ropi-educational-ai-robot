import os
import time
import hashlib
from pathlib import Path

import requests
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from openai import OpenAI

ROPI_SERVER_URL = "http://192.168.219.127:8000"

MIC_DEVICE_INDEX = 5
MIC_CHANNELS = 6

client = OpenAI()

BASE_DIR = Path(__file__).resolve().parent
RECORD_FILE = BASE_DIR / "voice_ai_command.wav"
ANSWER_FILE = BASE_DIR / "answer.mp3"
TTS_CACHE_DIR = BASE_DIR / "tts_cache"
TTS_CACHE_DIR.mkdir(exist_ok=True)

SAMPLE_RATE = 16000
RECORD_SECONDS = 3

LAST_COMMAND = None
LAST_COMMAND_TIME = 0
DUPLICATE_IGNORE_SECONDS = 3.0
COMMAND_COOLDOWN_SECONDS = 0.5

COMMAND_PATHS = {
    "status": "/status",
    "home": "/home",
    "walk": "/walk",
    "back": "/back",
    "left": "/left",
    "right": "/right",
    "stop": "/stop",
    "hello": "/say/hello",
}

TALK_PROMPT = """
너는 AI 로봇 캠프에서 사용하는 교육용 교구 로봇 '로피'다.

답변 규칙:
- 초등학생도 이해할 수 있게 쉽게 말한다.
- 답변은 2문장 이내로 짧게 한다.
- 어려운 용어는 쉬운 말로 바꾼다.
- 로피는 라즈베리파이, 서보모터, 초음파 센서, OpenAI API를 사용하는 교육용 로봇이다.
"""


def check_api_key():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print('OPENAI_API_KEY가 없습니다. export OPENAI_API_KEY="sk-..."')
        return False
    return True


def check_ropi_server():
    try:
        r = requests.get(ROPI_SERVER_URL + "/status", timeout=5)
        print("Ropi 서버:", r.status_code, r.text)
        return r.status_code == 200
    except requests.exceptions.RequestException as e:
        print("Ropi 서버 연결 실패:", e)
        return False


def record_audio():
    print(f"\n{RECORD_SECONDS}초 동안 듣는 중...")

    try:
        audio = sd.rec(
            int(RECORD_SECONDS * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=MIC_CHANNELS,
            dtype="int16",
            device=MIC_DEVICE_INDEX,
        )
        sd.wait()
    except Exception as e:
        print("녹음 오류:", e)
        return False

    if len(audio.shape) == 2 and audio.shape[1] > 1:
        mono = np.mean(audio, axis=1).astype("int16")
    else:
        mono = audio

    write(str(RECORD_FILE), SAMPLE_RATE, mono)
    return True


def transcribe_audio():
    try:
        with open(RECORD_FILE, "rb") as f:
            result = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=f,
                language="ko",
            )
        text = result.text.strip()
        print("인식:", text)
        return text
    except Exception as e:
        print("STT 오류:", e)
        return ""


def normalize_text(text):
    return text.replace(" ", "").replace(".", "").replace(",", "").replace("?", "").replace("!", "").lower()


def fast_route_user_text(user_text):
    text = normalize_text(user_text)

    if any(w in text for w in ["멈춰", "정지", "그만", "스톱", "stop"]):
        return {"type": "command", "command": "stop"}
    if any(w in text for w in ["앞으로", "전진", "앞으로가", "앞으로와"]):
        return {"type": "command", "command": "walk"}
    if any(w in text for w in ["뒤로", "후진", "뒤로가", "뒤로와"]):
        return {"type": "command", "command": "back"}
    if any(w in text for w in ["왼쪽", "좌회전", "왼쪽으로"]):
        return {"type": "command", "command": "left"}
    if any(w in text for w in ["오른쪽", "우회전", "오른쪽으로"]):
        return {"type": "command", "command": "right"}
    if any(w in text for w in ["기본자세", "처음자세", "제자리", "홈"]):
        return {"type": "command", "command": "home"}
    if any(w in text for w in ["인사", "안녕"]):
        return {"type": "command", "command": "hello"}
    if any(w in text for w in ["상태", "확인"]):
        return {"type": "command", "command": "status"}

    return {"type": "talk", "command": "unknown"}


def get_fast_answer(user_text):
    text = normalize_text(user_text)

    if any(w in text for w in ["자기소개", "너는누구", "누구야", "소개해줘"]):
        return "안녕하세요. 저는 AI 로봇 캠프에서 사용하는 교육용 로봇 로피입니다. 서보모터와 센서를 이용해서 움직이고, AI로 사람 말을 이해할 수 있어요."
    if any(w in text for w in ["ai가뭐야", "ai는뭐야", "인공지능"]):
        return "AI는 컴퓨터가 사람처럼 정보를 이해하고 판단하도록 돕는 기술이에요. 로피는 AI를 이용해서 사람 말을 알아듣고 대답할 수 있어요."
    if any(w in text for w in ["초음파센서", "초음파", "거리센서"]):
        return "초음파 센서는 소리를 보내고 다시 돌아오는 시간을 재서 거리를 아는 센서예요. 로피는 이 센서로 앞에 장애물이 있는지 확인할 수 있어요."
    if any(w in text for w in ["서보모터", "서보", "모터"]):
        return "서보모터는 원하는 각도로 움직일 수 있는 작은 모터예요. 로피는 서보모터로 다리와 발목을 움직여 걸어요."
    if any(w in text for w in ["어떻게걷", "걷는거야", "보행"]):
        return "로피는 다리와 발목의 서보모터를 조금씩 움직이면서 중심을 옮겨 걸어요. 로봇의 보행 원리를 보여줄 수 있어요."
    return None


def send_command_to_ropi(command):
    global LAST_COMMAND, LAST_COMMAND_TIME

    now = time.time()

    if command != "stop" and LAST_COMMAND == command and (now - LAST_COMMAND_TIME) < DUPLICATE_IGNORE_SECONDS:
        print("중복 명령 무시:", command)
        return

    url = ROPI_SERVER_URL + COMMAND_PATHS[command]
    print("명령 전송:", url)

    try:
        r = requests.get(url, timeout=40)
        print("응답:", r.status_code, r.text)
        LAST_COMMAND = command
        LAST_COMMAND_TIME = time.time()
        time.sleep(COMMAND_COOLDOWN_SECONDS)
    except requests.exceptions.RequestException as e:
        print("명령 전송 실패:", e)


def make_talk_answer(user_text):
    r = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": TALK_PROMPT},
            {"role": "user", "content": user_text},
        ],
    )
    return r.output_text.strip()


def make_tts_mp3_with_cache(text):
    h = hashlib.md5(text.encode("utf-8")).hexdigest()
    cached = TTS_CACHE_DIR / f"{h}.mp3"

    if cached.exists():
        print("TTS 캐시 사용:", cached)
        ANSWER_FILE.write_bytes(cached.read_bytes())
        return True

    try:
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text,
        ) as response:
            response.stream_to_file(cached)

        ANSWER_FILE.write_bytes(cached.read_bytes())
        return True
    except Exception as e:
        print("TTS 오류:", e)
        return False


def upload_answer_to_ropi():
    with open(ANSWER_FILE, "rb") as f:
        files = {"file": ("answer.mp3", f, "audio/mpeg")}
        r = requests.post(ROPI_SERVER_URL + "/upload_speech", files=files, timeout=60)
    print("업로드:", r.status_code, r.text)
    return r.status_code == 200


def play_uploaded_on_ropi():
    r = requests.get(ROPI_SERVER_URL + "/play_uploaded", timeout=60)
    print("재생:", r.status_code, r.text)


def play_wait_sync():
    try:
        r = requests.get(ROPI_SERVER_URL + "/say/wait", timeout=30)
        print("wait:", r.status_code, r.text)
    except requests.exceptions.RequestException as e:
        print("wait 실패:", e)


def handle_talk(user_text):
    play_wait_sync()

    answer = get_fast_answer(user_text)
    if answer:
        print("빠른 답변:", answer)
    else:
        answer = make_talk_answer(user_text)
        print("AI 답변:", answer)

    if not make_tts_mp3_with_cache(answer):
        return
    if not upload_answer_to_ropi():
        return
    play_uploaded_on_ropi()


def main():
    if not check_api_key():
        return
    if not check_ropi_server():
        return

    print("Ropi 시연 클라이언트 시작")
    print("명령 예: 앞으로 가 / 멈춰 / AI가 뭐야?")

    try:
        while True:
            if not record_audio():
                continue

            text = transcribe_audio()
            if not text:
                continue

            routed = fast_route_user_text(text)
            print("분류:", routed)

            if routed["type"] == "command":
                send_command_to_ropi(routed["command"])
            else:
                handle_talk(text)

            time.sleep(0.3)

    except KeyboardInterrupt:
        print("종료")


if __name__ == "__main__":
    main()
