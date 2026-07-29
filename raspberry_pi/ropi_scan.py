"""채널을 하나씩 돌려보며 어디에 무엇이 붙어 있는지 찾는다.

    python3 raspberry_pi/ropi_scan.py          # 4~15 (팔 찾기)
    python3 raspberry_pi/ropi_scan.py 0 15     # 전체

화면에 뜬 채널 번호를 보면서 어느 모터가 움직이는지 눈으로 확인하면 된다.
바퀴(CH2, CH3)는 기본적으로 건너뛴다. 로봇이 굴러가면 관찰이 어렵다.
"""
import sys
import time

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import ropi_motion as m

POWER = 80      # 최대에 가깝게. 데드밴드 때문에 안 도는 경우를 배제한다.
HOLD = 1.2
SKIP = {m.LEFT_WHEEL, m.RIGHT_WHEEL}


def main():
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 15

    print(f"CH{start} ~ CH{end} 를 하나씩 돌립니다. 출력 {POWER}.")
    print("바퀴(CH2,3)는 건너뜁니다. Ctrl-C 로 중단.\n")

    touched = []
    try:
        for ch in range(start, end + 1):
            if ch in SKIP:
                print(f"  CH{ch:<2} 건너뜀 (바퀴)")
                continue
            m.CENTER.setdefault(ch, 90)
            m.DIRECTION.setdefault(ch, 1)
            touched.append(ch)

            print(f"\n>>> CH{ch} <<<   지금 이 채널을 돌립니다", flush=True)
            for off, label in ((POWER, "정방향"), (-POWER, "역방향")):
                print(f"    {label}", flush=True)
                m.move_servo(ch, off)
                time.sleep(HOLD)
                m.stop_channels([ch])
                time.sleep(0.5)
    finally:
        m.stop_channels(touched)
        m.stop()
        print("\n전부 정지.")


if __name__ == "__main__":
    main()
