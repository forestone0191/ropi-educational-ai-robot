import os
from pathlib import Path
from openai import OpenAI

client = OpenAI()
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "wait.mp3"

WAIT_TEXT = "Okay, please wait."


def main():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print('OPENAI_API_KEY가 없습니다. export OPENAI_API_KEY="sk-..."')
        return

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=WAIT_TEXT,
    ) as response:
        response.stream_to_file(OUTPUT_FILE)

    print("생성 완료:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
