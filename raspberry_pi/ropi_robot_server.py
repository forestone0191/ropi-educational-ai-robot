import subprocess
import threading
import time
from pathlib import Path

import RPi.GPIO as GPIO
from fastapi import FastAPI, UploadFile, File

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

MOTION_FILE = BASE_DIR / "ropi_motion.py"
SPEAKER_FILE = BASE_DIR / "ropi_speaker.py"

SOUND_DIR = PROJECT_DIR / "sounds"
SOUND_DIR.mkdir(exist_ok=True)

UPLOAD_DIR = PROJECT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

TRIG_PIN = 23
ECHO_PIN = 24
OBSTACLE_DISTANCE_CM = 10.0
ULTRASONIC_CHECK_INTERVAL = 0.12

app = FastAPI(title="Ropi Robot Server")

motion_thread = None
sensor_thread = None
motion_stop_event = threading.Event()
sensor_stop_event = threading.Event()
motion_lock = threading.Lock()

current_motion = None
last_distance_cm = None
obstacle_detected = False


def setup_ultrasonic():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    GPIO.output(TRIG_PIN, False)
    time.sleep(0.2)


def get_distance_cm():
    try:
        GPIO.output(TRIG_PIN, False)
        time.sleep(0.0002)

        GPIO.output(TRIG_PIN, True)
        time.sleep(0.00001)
        GPIO.output(TRIG_PIN, False)

        timeout_start = time.time()
        pulse_start = time.time()

        while GPIO.input(ECHO_PIN) == 0:
            pulse_start = time.time()
            if pulse_start - timeout_start > 0.03:
                return None

        timeout_start = time.time()
        pulse_end = time.time()

        while GPIO.input(ECHO_PIN) == 1:
            pulse_end = time.time()
            if pulse_end - timeout_start > 0.03:
                return None

        distance_cm = (pulse_end - pulse_start) * 34300 / 2

        if distance_cm <= 0 or distance_cm > 400:
            return None

        return distance_cm
    except Exception:
        return None


def run_python_script(script_path, *args, timeout=40):
    if not script_path.exists():
        return {"ok": False, "error": f"File not found: {script_path}"}

    try:
        result = subprocess.run(
            ["python3", str(script_path), *args],
            cwd=str(PROJECT_DIR),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "ok": result.returncode == 0,
            "command": ["python3", str(script_path), *args],
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Command timeout"}


def motion_loop(command):
    global current_motion
    current_motion = command
    print("[motion_loop] start:", command)

    while not motion_stop_event.is_set():
        result = run_python_script(MOTION_FILE, command, timeout=20)
        print("[motion_loop]", command, result)
        time.sleep(0.05)

    current_motion = None
    print("[motion_loop] end:", command)


def ultrasonic_monitor_loop():
    global last_distance_cm, obstacle_detected
    print("[ultrasonic] start")

    while not sensor_stop_event.is_set():
        distance = get_distance_cm()
        last_distance_cm = distance

        if distance is not None:
            print(f"[ultrasonic] {distance:.1f} cm")

            if distance <= OBSTACLE_DISTANCE_CM:
                print("[ultrasonic] obstacle detected. auto stop")
                obstacle_detected = True
                motion_stop_event.set()
                run_python_script(MOTION_FILE, "stop", timeout=20)
                break

        time.sleep(ULTRASONIC_CHECK_INTERVAL)

    print("[ultrasonic] end")


def stop_current_motion():
    global motion_thread, sensor_thread, current_motion

    with motion_lock:
        motion_stop_event.set()
        sensor_stop_event.set()

        if motion_thread is not None and motion_thread.is_alive():
            motion_thread.join(timeout=3)

        if sensor_thread is not None and sensor_thread.is_alive():
            sensor_thread.join(timeout=3)

        motion_thread = None
        sensor_thread = None
        current_motion = None

        return run_python_script(MOTION_FILE, "stop", timeout=20)


def start_continuous_motion(command):
    global motion_thread, sensor_thread, current_motion, obstacle_detected

    if command not in ["walk", "back", "left", "right"]:
        return {"ok": False, "error": f"Invalid motion: {command}"}

    with motion_lock:
        motion_stop_event.set()
        sensor_stop_event.set()

        if motion_thread is not None and motion_thread.is_alive():
            motion_thread.join(timeout=3)
        if sensor_thread is not None and sensor_thread.is_alive():
            sensor_thread.join(timeout=3)

        obstacle_detected = False
        motion_stop_event.clear()
        sensor_stop_event.clear()

        setup_ultrasonic()

        motion_thread = threading.Thread(target=motion_loop, args=(command,), daemon=True)
        sensor_thread = threading.Thread(target=ultrasonic_monitor_loop, daemon=True)

        motion_thread.start()
        sensor_thread.start()

        current_motion = command

    return {
        "ok": True,
        "message": f"{command} continuous motion started",
        "current_motion": current_motion,
        "ultrasonic_enabled": True,
        "obstacle_distance_cm": OBSTACLE_DISTANCE_CM,
    }


@app.get("/")
def root():
    return {"message": "Ropi Robot Server is running"}


@app.get("/status")
def status():
    return {
        "ok": True,
        "robot": "Ropi",
        "server": "running",
        "mode": "continuous_motion_with_ultrasonic",
        "current_motion": current_motion,
        "motion_thread_alive": motion_thread is not None and motion_thread.is_alive(),
        "sensor_thread_alive": sensor_thread is not None and sensor_thread.is_alive(),
        "last_distance_cm": last_distance_cm,
        "obstacle_detected": obstacle_detected,
    }


@app.get("/distance")
def distance():
    setup_ultrasonic()
    d = get_distance_cm()
    return {
        "ok": d is not None,
        "distance_cm": d,
        "obstacle_distance_cm": OBSTACLE_DISTANCE_CM,
        "obstacle": d is not None and d <= OBSTACLE_DISTANCE_CM,
    }


@app.get("/home")
def home():
    stop_current_motion()
    return run_python_script(MOTION_FILE, "home")


@app.get("/walk")
def walk():
    return start_continuous_motion("walk")


@app.get("/back")
def back():
    return start_continuous_motion("back")


@app.get("/left")
def left():
    return start_continuous_motion("left")


@app.get("/right")
def right():
    return start_continuous_motion("right")


@app.get("/stop")
def stop():
    result = stop_current_motion()
    return {"ok": True, "message": "Ropi motion stopped", "stop_result": result}


@app.get("/say/{voice_name}")
def say(voice_name: str):
    allowed = {"hello", "start", "obstacle", "stop", "wait"}
    if voice_name not in allowed:
        return {"ok": False, "error": f"Unsupported voice: {voice_name}"}
    return run_python_script(SPEAKER_FILE, voice_name)


@app.post("/upload_speech")
async def upload_speech(file: UploadFile = File(...)):
    output_path = UPLOAD_DIR / "answer.mp3"
    content = await file.read()
    output_path.write_bytes(content)
    return {"ok": True, "saved_to": str(output_path), "size": len(content)}


@app.get("/play_uploaded")
def play_uploaded():
    file_path = UPLOAD_DIR / "answer.mp3"
    if not file_path.exists():
        return {"ok": False, "error": f"Uploaded file not found: {file_path}"}

    try:
        result = subprocess.run(
            ["mpg123", "-q", str(file_path)],
            cwd=str(PROJECT_DIR),
            capture_output=True,
            text=True,
            timeout=60,
        )
        return {"ok": result.returncode == 0, "stderr": result.stderr}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Playback timeout"}


@app.post("/upload_wait")
async def upload_wait(file: UploadFile = File(...)):
    output_path = SOUND_DIR / "wait.mp3"
    content = await file.read()
    output_path.write_bytes(content)
    return {"ok": True, "saved_to": str(output_path), "size": len(content)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("raspberry_pi.ropi_robot_server:app", host="0.0.0.0", port=8000, reload=False)
