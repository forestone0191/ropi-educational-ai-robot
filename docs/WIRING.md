# Ropi 배선

## PCA9685

| PCA9685 | Raspberry Pi |
|---|---|
| VCC | 3.3V |
| GND | GND |
| SDA | GPIO2 |
| SCL | GPIO3 |

## 서보 채널

| 역할 | 채널 |
|---|---|
| LEFT_LEG | CH0 |
| RIGHT_LEG | CH1 |
| LEFT_FOOT | CH2 |
| RIGHT_FOOT | CH3 |

## HC-SR04

| HC-SR04 | Raspberry Pi |
|---|---|
| VCC | 5V |
| GND | GND |
| TRIG | GPIO23 |
| ECHO | 저항 분압 후 GPIO24 |

Echo는 5V이므로 Raspberry Pi GPIO에 직접 연결하지 마세요.
