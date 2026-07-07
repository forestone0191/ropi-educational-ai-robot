#!/usr/bin/env bash
set -e
sudo apt update
sudo apt install -y python3-pip python3-venv i2c-tools mpg123
cd "$(dirname "$0")/.."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r raspberry_pi/requirements.txt
mkdir -p sounds uploads
echo "완료. I2C는 sudo raspi-config 에서 활성화하세요."
