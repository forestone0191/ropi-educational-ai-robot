#!/usr/bin/env python3
"""OPENAI_API_KEY 가 이 프로젝트에서 실제로 쓸 수 있는지 확인한다."""
import os
import sys
import tempfile
from pathlib import Path

STT_MODEL = "gpt-4o-mini-transcribe"
TALK_MODEL = "gpt-4.1-mini"
TTS_MODEL = "gpt-4o-mini-tts"


def make_test_wav(path, seconds=1.0, rate=16000):
    import struct
    import wave
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"".join(
            struct.pack("<h", int(300 * ((i // 40) % 2 * 2 - 1)))
            for i in range(int(rate * seconds))))


def main():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("❌ OPENAI_API_KEY 가 설정되지 않았습니다.")
        return 1
    print(f"키 확인: {key[:8]}... (총 {len(key)}자)")
    if not key.isascii():
        print("❌ 키에 ASCII 가 아닌 문자가 있습니다. 예시 문구를 넣으신 것 같습니다.")
        return 1
    if len(key) < 40:
        print(f"❌ 키가 너무 짧습니다({len(key)}자).")
        return 1

    from openai import OpenAI
    client = OpenAI()
    results = {}

    print(f"\n[1/3] 대화 {TALK_MODEL} ...")
    try:
        r = client.responses.create(
            model=TALK_MODEL,
            input=[{"role": "user", "content": "한 단어로만 대답해: 안녕"}])
        print(f"   ✅ {r.output_text.strip()[:30]}")
        results["대화"] = True
    except Exception as e:
        print(f"   ❌ {type(e).__name__}: {str(e)[:160]}")
        results["대화"] = False

    print(f"\n[2/3] 음성합성 {TTS_MODEL} ...")
    out = Path(tempfile.gettempdir()) / "ropi_tts_check.mp3"
    try:
        with client.audio.speech.with_streaming_response.create(
                model=TTS_MODEL, voice="alloy", input="테스트입니다.") as resp:
            resp.stream_to_file(out)
        print(f"   ✅ mp3 {out.stat().st_size:,} 바이트")
        results["음성합성"] = True
    except Exception as e:
        print(f"   ❌ {type(e).__name__}: {str(e)[:160]}")
        results["음성합성"] = False

    print(f"\n[3/3] 음성인식 {STT_MODEL} ...")
    wav = Path(tempfile.gettempdir()) / "ropi_stt_check.wav"
    try:
        make_test_wav(wav)
        with open(wav, "rb") as f:
            client.audio.transcriptions.create(model=STT_MODEL, file=f, language="ko")
        print("   ✅ 호출 성공")
        results["음성인식"] = True
    except Exception as e:
        print(f"   ❌ {type(e).__name__}: {str(e)[:160]}")
        results["음성인식"] = False

    print("\n" + "=" * 40)
    for name, ok in results.items():
        print(f"  {name:8} {'✅ 사용 가능' if ok else '❌ 사용 불가'}")
    print("=" * 40)
    if all(results.values()):
        print("\n전부 정상입니다. 로피를 실행할 수 있습니다.")
        return 0
    print("\n실패 항목이 있습니다. 크레딧 잔액과 키 권한을 확인하세요.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
