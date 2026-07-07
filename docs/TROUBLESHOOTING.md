# 문제 해결

## 서버 확인

```bash
curl http://라즈베리파이IP:8000/status
```

## 초음파 확인

```bash
curl http://라즈베리파이IP:8000/distance
```

## 긴급 정지

```bash
curl http://라즈베리파이IP:8000/stop
```

## ReSpeaker 확인

```bash
python3 laptop/list_audio_devices.py
```

장치 번호가 바뀌면 `ropi_voice_ai_client.py`의 `MIC_DEVICE_INDEX`, `MIC_CHANNELS`를 수정하세요.
