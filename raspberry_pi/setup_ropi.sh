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
# 갓 부팅한 파이는 packagekitd 가 자동 업데이트를 돌리느라 apt 를 잡고 있다.
# 그 상태에서 apt 를 부르면 lock 에러로 죽는다. 끝날 때까지 기다린다.
wait_for_apt() {
    local waited=0
    while sudo fuser /var/lib/dpkg/lock-frontend \
                     /var/lib/apt/lists/lock >/dev/null 2>&1; do
        if [ "$waited" -eq 0 ]; then
            echo "  다른 프로그램이 apt 를 쓰는 중입니다. 기다립니다..."
        fi
        if [ "$waited" -ge 120 ]; then
            echo "  2분이 지나 자동 업데이트를 중지시킵니다."
            sudo systemctl stop packagekit 2>/dev/null || true
            sudo pkill -x packagekitd 2>/dev/null || true
            sleep 3
            break
        fi
        sleep 5
        waited=$((waited + 5))
    done
}

wait_for_apt
sudo apt-get update -qq
wait_for_apt
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    i2c-tools python3-venv python3-full

echo "=== 3. I2C 장치 확인 ==="
if [ ! -e /dev/i2c-1 ]; then
    echo "  !! /dev/i2c-1 이 없습니다. 재부팅 후 다시 실행하세요."
    exit 1
fi
echo "  /dev/i2c-1 OK"

echo "=== 4. PCA9685 확인 ==="
# -r 을 붙여 '읽기'로 두드린다.
# 기본 방식(빈 쓰기)에는 응답하지 않는 PCA9685 개체가 있어서,
# 배선이 멀쩡한데도 없는 것으로 나오는 일이 있었다.
scan_i2c() {
    /usr/sbin/i2cdetect -y -r 1 | tail -n +2 | cut -d: -f2- \
        | tr ' ' '\n' | grep -E '^40$' || true
}
FOUND=$(scan_i2c)
if [ -z "$FOUND" ]; then
    echo "  0x40 이 안 잡혀 한 번 더 시도합니다..."
    sleep 2
    FOUND=$(scan_i2c)
fi
if [ -z "$FOUND" ]; then
    echo "  !! PCA9685 를 못 찾았습니다. 아래를 확인하세요."
    echo "     - VCC (로직 전원) 가 꽂혀 있는지. V+ (서보 전원) 와 다른 핀이다."
    echo "     - SDA(파이 3번핀) / SCL(파이 5번핀) 이 바뀌지 않았는지"
    echo "     - GND 가 공통으로 연결되어 있는지"
    /usr/sbin/i2cdetect -y -r 1
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
