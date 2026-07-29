#!/usr/bin/env bash
# ROPI 라즈베리파이 세팅. 새 보드에서 한 번만 실행하면 된다.
#
#   bash setup_ropi.sh            # 세팅만
#   bash setup_ropi.sh ropi02     # 세팅 + 호스트이름 변경
#
# 호스트이름을 주면 재부팅 후 <이름>.local 로 접속할 수 있다.
# 로봇이 여러 대일 때 IP 를 찾아다니지 않아도 되므로 이름을 주는 편이 낫다.
set -e

NEW_HOSTNAME="$1"
PROJECT="$HOME/ropi_robot"

echo "=== 1. I2C 활성화 ==="
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_wifi_country KR 2>/dev/null || true

echo "=== 2. 패키지 설치 ==="
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    i2c-tools python3-venv python3-full

echo "=== 3. I2C 장치 확인 ==="
if [ ! -e /dev/i2c-1 ]; then
    echo "  !! /dev/i2c-1 이 없습니다. 재부팅 후 다시 실행하세요."
    exit 1
fi
echo "  /dev/i2c-1 OK"

echo "=== 4. PCA9685 확인 ==="
FOUND=$(/usr/sbin/i2cdetect -y 1 | tail -n +2 | cut -d: -f2- \
        | tr ' ' '\n' | grep -E '^40$' || true)
if [ -z "$FOUND" ]; then
    echo "  !! 0x40 이 안 잡힙니다. PCA9685 배선(SDA/SCL/전원)을 확인하세요."
    /usr/sbin/i2cdetect -y 1
    exit 1
fi
echo "  PCA9685 (0x40) 감지됨"

echo "=== 5. 파이썬 환경 ==="
mkdir -p "$PROJECT/raspberry_pi"
cd "$PROJECT"
[ -d venv ] || python3 -m venv venv
./venv/bin/pip install -q --upgrade pip
./venv/bin/pip install -q -r raspberry_pi/requirements.txt
./venv/bin/python3 -c "import adafruit_servokit, fastapi, uvicorn; print('  라이브러리 OK')"

echo "=== 6. 모터 정지 상태 확인 ==="
./venv/bin/python3 - <<'PY'
import sys
sys.path.insert(0, "raspberry_pi")
import ropi_motion as m
m.stop()
print("  전 채널 PWM 차단 (모터 안 움직임)")
PY

if [ -n "$NEW_HOSTNAME" ]; then
    echo "=== 7. 호스트이름 -> $NEW_HOSTNAME ==="
    sudo raspi-config nonint do_hostname "$NEW_HOSTNAME"
    echo ""
    echo "세팅 완료. 재부팅하면 $NEW_HOSTNAME.local 로 접속됩니다."
    echo "  sudo reboot"
else
    echo ""
    echo "세팅 완료. 현재 주소: $(hostname -I)"
fi

echo ""
echo "조종하려면:"
echo "  cd ~/ropi_robot && source venv/bin/activate && python3 raspberry_pi/ropi_teleop.py"
