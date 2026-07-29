"""채널 하나만 최대 출력으로 양방향 테스트.

    python3 raspberry_pi/ropi_ch.py 2

서보 고장인지 채널 고장인지 가르는 데 쓴다.
의심되는 서보를 정상 채널에 꽂아보고, 정상 서보를 의심 채널에 꽂아보면
문제가 서보를 따라가는지 채널에 남는지 알 수 있다.
"""
import sys
import time

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import ropi_motion as m


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 ropi_ch.py <채널 0-15>")
        return
    ch = int(sys.argv[1])
    if ch not in m.CENTER:
        m.CENTER[ch] = 90
        m.DIRECTION[ch] = 1

    print(f"CH{ch} 테스트. 정지하려면 Ctrl-C.\n")
    try:
        for i in range(4):
            for off, label in ((90, "정방향"), (-90, "역방향")):
                print(f"  {i+1}회차 {label} (최대 출력) 1.5초", flush=True)
                m.move_servo(ch, off)
                time.sleep(1.5)
                m.stop_channels([ch])
                time.sleep(0.6)
    finally:
        m.stop_channels([ch])
        print("\n정지.")


if __name__ == "__main__":
    main()
