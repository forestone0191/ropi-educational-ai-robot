# Ropi 교육용 AI 로봇

Ropi는 AI 로봇 캠프에서 사용할 수 있도록 만든 교육용 보행 로봇입니다.

## 주요 기능
- Raspberry Pi 3 B+ + PCA9685 + SG90 4개 서보모터 제어
- 앞으로 / 뒤로 / 왼쪽 / 오른쪽 연속 이동
- `멈춰` 명령 전까지 계속 움직임
- HC-SR04 초음파 센서로 전방 10cm 이내 장애물 감지 시 자동 정지
- 노트북 ReSpeaker 마이크 + OpenAI STT/TTS
- AI, 초음파 센서, 서보모터, 보행 원리 설명

## 폴더 구조

```text
ropi
├─ raspberry_pi
│  ├─ ropi_motion.py
│  ├─ ropi_speaker.py
│  ├─ ropi_robot_server.py
│  ├─ requirements.txt
│  └─ setup_pi.sh
├─ laptop
│  ├─ list_audio_devices.py
│  ├─ make_wait_voice.py
│  ├─ upload_wait.py
│  ├─ ropi_voice_ai_client.py
│  ├─ requirements.txt
│  └─ setup_laptop.sh
├─ docs
│  ├─ DEMO_GUIDE.md
│  ├─ WIRING.md
│  └─ TROUBLESHOOTING.md
├─ sounds
├─ uploads
└─ README.md
```

## Raspberry Pi 실행

```bash
cd ~/ropi_robot
source venv/bin/activate
uvicorn raspberry_pi.ropi_robot_server:app --host 0.0.0.0 --port 8000
```

## Laptop 실행

`laptop/ropi_voice_ai_client.py`에서 Raspberry Pi IP를 수정합니다.

```python
ROPI_SERVER_URL = "http://라즈베리파이IP:8000"
```

실행:

```bash
cd ~/ropi_laptop
source venv/bin/activate
python3 laptop/ropi_voice_ai_client.py
```

## 시연 음성 순서

```text
자기소개해줘
AI가 뭐야?
초음파 센서는 뭐야?
서보모터 설명해줘
앞으로 가
멈춰
뒤로 가
멈춰
왼쪽으로 돌아
멈춰
오른쪽으로 돌아
멈춰
앞으로 가
```

마지막 `앞으로 가`에서 로피 앞 10cm 이내에 물체를 놓으면 자동 정지합니다.

## License / 사용권

This project is not open source.

Ropi is publicly visible for educational reference, but commercial use, redistribution,
manufacturing, paid classes, derivative kits, and institutional use are prohibited without
prior written permission.

See `LICENSE` and `LICENSE-KO.md` for details.

본 프로젝트는 오픈소스가 아닙니다.

Ropi는 교육 참고 목적으로 공개되어 있으나, 저작권자의 사전 서면 허가 없이 상업적 사용,
재배포, 교구 제작·판매, 유료 수업 운영, 기관 교육 사용, 파생 키트 제작을 할 수 없습니다.

자세한 내용은 `LICENSE` 및 `LICENSE-KO.md`를 확인하세요.
