import sys
import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

LEFT_LEG = 0
RIGHT_LEG = 1
LEFT_FOOT = 2
RIGHT_FOOT = 3

CENTER = {LEFT_LEG: 90, RIGHT_LEG: 90, LEFT_FOOT: 90, RIGHT_FOOT: 90}
DIRECTION = {LEFT_LEG: 1, RIGHT_LEG: -1, LEFT_FOOT: 1, RIGHT_FOOT: -1}

LEG_STEP = 22
FOOT_TILT = 18
SHORT_HOLD = 0.10
NORMAL_HOLD = 0.14


def clamp(angle):
    return max(0, min(180, angle))


def set_servo(channel, angle):
    kit.servo[channel].angle = clamp(angle)


def move_servo(channel, offset):
    set_servo(channel, CENTER[channel] + offset * DIRECTION[channel])


def home():
    for ch in [LEFT_LEG, RIGHT_LEG, LEFT_FOOT, RIGHT_FOOT]:
        set_servo(ch, CENTER[ch])
    time.sleep(0.2)


def stop():
    home()


def tilt_left():
    move_servo(LEFT_FOOT, -FOOT_TILT)
    move_servo(RIGHT_FOOT, -FOOT_TILT)
    time.sleep(SHORT_HOLD)


def tilt_right():
    move_servo(LEFT_FOOT, FOOT_TILT)
    move_servo(RIGHT_FOOT, FOOT_TILT)
    time.sleep(SHORT_HOLD)


def feet_center():
    move_servo(LEFT_FOOT, 0)
    move_servo(RIGHT_FOOT, 0)
    time.sleep(SHORT_HOLD)


def legs_center():
    move_servo(LEFT_LEG, 0)
    move_servo(RIGHT_LEG, 0)
    time.sleep(SHORT_HOLD)


def walk():
    tilt_left()
    move_servo(RIGHT_LEG, LEG_STEP)
    move_servo(LEFT_LEG, LEG_STEP)
    time.sleep(NORMAL_HOLD)
    feet_center()
    legs_center()

    tilt_right()
    move_servo(RIGHT_LEG, -LEG_STEP)
    move_servo(LEFT_LEG, -LEG_STEP)
    time.sleep(NORMAL_HOLD)
    feet_center()
    legs_center()


def back():
    tilt_left()
    move_servo(RIGHT_LEG, -LEG_STEP)
    move_servo(LEFT_LEG, -LEG_STEP)
    time.sleep(NORMAL_HOLD)
    feet_center()
    legs_center()

    tilt_right()
    move_servo(RIGHT_LEG, LEG_STEP)
    move_servo(LEFT_LEG, LEG_STEP)
    time.sleep(NORMAL_HOLD)
    feet_center()
    legs_center()


def turn_left():
    tilt_left()
    move_servo(RIGHT_LEG, LEG_STEP)
    move_servo(LEFT_LEG, -LEG_STEP)
    time.sleep(NORMAL_HOLD)
    feet_center()
    legs_center()

    tilt_right()
    move_servo(RIGHT_LEG, LEG_STEP)
    move_servo(LEFT_LEG, -LEG_STEP)
    time.sleep(NORMAL_HOLD)
    feet_center()
    legs_center()


def turn_right():
    tilt_left()
    move_servo(RIGHT_LEG, -LEG_STEP)
    move_servo(LEFT_LEG, LEG_STEP)
    time.sleep(NORMAL_HOLD)
    feet_center()
    legs_center()

    tilt_right()
    move_servo(RIGHT_LEG, -LEG_STEP)
    move_servo(LEFT_LEG, LEG_STEP)
    time.sleep(NORMAL_HOLD)
    feet_center()
    legs_center()


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 ropi_motion.py home|walk|back|left|right|stop")
        return

    command = sys.argv[1].lower()
    if command == "home":
        home()
    elif command == "walk":
        walk()
    elif command == "back":
        back()
    elif command == "left":
        turn_left()
    elif command == "right":
        turn_right()
    elif command == "stop":
        stop()
    else:
        print("Unknown command:", command)


if __name__ == "__main__":
    main()
