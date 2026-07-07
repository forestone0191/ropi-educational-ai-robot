# Ropi 시연 순서

## 실행 명령

### Raspberry Pi

```bash
cd ~/ropi_robot
source venv/bin/activate
uvicorn raspberry_pi.ropi_robot_server:app --host 0.0.0.0 --port 8000
```

### Laptop

```bash
cd ~/ropi_laptop
source venv/bin/activate
python3 laptop/ropi_voice_ai_client.py
```

## 점검 명령

```bash
curl http://라즈베리파이IP:8000/status
curl http://라즈베리파이IP:8000/distance
curl http://라즈베리파이IP:8000/say/hello
curl http://라즈베리파이IP:8000/stop
```

## 음성 시연 순서

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

마지막 앞으로 가에서 앞 10cm 이내에 물체를 놓으면 자동 정지합니다.
