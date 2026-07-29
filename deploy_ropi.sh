#!/usr/bin/env bash
# 맥에서 실행. 새 로피 보드 한 대를 처음부터 끝까지 세팅한다.
#
#   bash deploy_ropi.sh 192.168.0.77            # 세팅만
#   bash deploy_ropi.sh 192.168.0.77 ropi02     # 세팅 + 이름 변경
#
# 보드가 와이파이에 붙어 있고 SSH 가 켜져 있어야 한다.
# 그 두 가지는 모니터+키보드를 붙여서 먼저 해줘야 한다.
set -e

TARGET="$1"
NEW_HOSTNAME="$2"
USER_NAME="${ROPI_USER:-stone0191}"
SRC="$(cd "$(dirname "$0")" && pwd)/raspberry_pi"

if [ -z "$TARGET" ]; then
    echo "사용법: bash deploy_ropi.sh <IP 또는 이름> [새 호스트이름]"
    exit 1
fi

HOST="$USER_NAME@$TARGET"

echo "=== 1. 연결 확인: $HOST ==="
if ! ssh -o ConnectTimeout=8 -o BatchMode=yes "$HOST" true 2>/dev/null; then
    echo "  SSH 키가 없습니다. 지금 등록합니다 (비밀번호를 물어봅니다)"
    ssh-copy-id -o StrictHostKeyChecking=accept-new "$HOST"
fi
echo "  접속 OK"

echo "=== 2. 코드 복사 ==="
ssh "$HOST" 'mkdir -p ~/ropi_robot/raspberry_pi'
scp -q "$SRC"/*.py "$SRC"/requirements.txt "$SRC"/setup_ropi.sh \
    "$HOST:~/ropi_robot/raspberry_pi/"
echo "  복사 완료"

echo "=== 3. 보드 세팅 ==="
# ropi_drive.json 은 보내지 않는다. 서보 개체차가 있어 보정값은 로봇마다 다르다.
ssh -t "$HOST" "cd ~/ropi_robot/raspberry_pi && bash setup_ropi.sh $NEW_HOSTNAME"

echo ""
echo "=== 완료 ==="
if [ -n "$NEW_HOSTNAME" ]; then
    echo "재부팅 후 접속:  ssh $USER_NAME@$NEW_HOSTNAME.local"
    echo "  ssh $HOST 'sudo reboot'"
fi
echo "조종:"
echo "  ssh -t $HOST 'cd ~/ropi_robot && source venv/bin/activate && python3 raspberry_pi/ropi_teleop.py'"
