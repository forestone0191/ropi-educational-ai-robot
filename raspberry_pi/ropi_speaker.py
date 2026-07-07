import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
SOUND_DIR = PROJECT_DIR / "sounds"

SOUND_FILES = {
    "hello": "hello.mp3",
    "start": "start.mp3",
    "obstacle": "obstacle.mp3",
    "stop": "stop.mp3",
    "wait": "wait.mp3",
}


def play_mp3(file_path):
    if not file_path.exists():
        print(f"Audio file not found: {file_path}")
        return False

    try:
        subprocess.run(["mpg123", "-q", str(file_path)], check=True)
        return True
    except FileNotFoundError:
        print("mpg123 is not installed. Run: sudo apt install -y mpg123")
        return False
    except subprocess.CalledProcessError:
        print("mp3 playback error")
        return False


def speak(command):
    if command not in SOUND_FILES:
        print("Unknown voice command:", command)
        return False

    file_path = SOUND_DIR / SOUND_FILES[command]
    print("Playing:", file_path)
    return play_mp3(file_path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 ropi_speaker.py hello|start|obstacle|stop|wait")
        return

    speak(sys.argv[1].lower())


if __name__ == "__main__":
    main()
