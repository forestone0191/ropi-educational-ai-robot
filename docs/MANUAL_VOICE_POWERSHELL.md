# 로피 음성 AI 매뉴얼 — 윈도우 (PowerShell)

**말로 로봇을 움직이는 방법**입니다. "앞으로 가", "공격해" 처럼 말하면 로봇이 알아듣습니다.

먼저 [키보드 조종](MANUAL_WINDOWS_POWERSHELL.md)이 되는지 확인하고 오세요.
그게 안 되면 음성도 안 됩니다.

> **WSL로 하지 마세요.** WSL은 마이크에 접근할 수 없습니다.
> 음성 프로그램이라 **윈도우 파이썬으로 직접 돌려야** 합니다.

---

## 어떻게 움직이는지

```
내 목소리 ──> 노트북 ──> OpenAI ──> 노트북 ──> 로봇
             (마이크)   (알아듣기)  (명령 보내기)
```

**노트북이 듣고, AI가 알아듣고, 노트북이 로봇에게 명령을 보냅니다.**
로봇은 명령만 받습니다. 그래서 노트북과 로봇이 **같은 와이파이**에 있어야 합니다.

---

## 준비물

| 항목 | 적는 곳 |
|---|---|
| 내 로봇 IP | `192.168.____.____` |
| 로봇 비밀번호 | |
| OpenAI API 키 | 선생님께 받으세요 |

- 마이크가 있는 노트북 (내장 마이크로 충분합니다)
- 스피커 또는 이어폰

---

## 1단계 — 파이썬 설치 (처음 한 번만)

PowerShell을 열고 아래를 칩니다.

```powershell
python --version
```

`Python 3.11.x` 같은 게 나오면 **2단계로 가세요.**

<details>
<summary>아무것도 안 나오거나 Microsoft Store가 열리면 (눌러서 펼치기)</summary>

파이썬이 없는 겁니다. 둘 중 하나로 설치하세요.

**방법 A — 명령으로 (권장)**

```powershell
winget install Python.Python.3.12
```

설치가 끝나면 **PowerShell을 닫고 새로 열어야** 합니다.

**방법 B — 직접 내려받기**

<https://www.python.org/downloads/> 에서 내려받아 설치합니다.

> 설치 화면 맨 아래 **`Add python.exe to PATH`** 를 꼭 체크하세요.
> 이걸 안 하면 `python` 명령을 못 찾습니다.

</details>

---

## 2단계 — 코드 받기 (처음 한 번만)

> **깃허브 계정을 만들 필요 없습니다.** 공개된 코드는 누구나 그냥 받을 수 있습니다.
> 로그인 화면도 안 뜹니다. 계정이 필요한 건 코드를 **올릴** 때뿐입니다.

```powershell
cd ~
git clone https://github.com/forestone0191/ropi-educational-ai-robot.git
cd ropi-educational-ai-robot\laptop
```

<details>
<summary>git이 없다고 나오면</summary>

```powershell
winget install Git.Git
```

설치 후 PowerShell을 새로 열고 다시 하세요.

**또는** GitHub 페이지에서 `Code` → `Download ZIP` 으로 내려받아 압축을 풀어도 됩니다.

</details>

---

## 3단계 — 필요한 프로그램 설치 (처음 한 번만)

`laptop` 폴더 안에서 실행합니다.

```powershell
python -m pip install --upgrade pip
```

```powershell
python -m pip install -r requirements.txt
```

`openai`, `requests`, `sounddevice`, `numpy`, `scipy` 다섯 개가 깔립니다. 2~3분 걸립니다.

> **마이크 관련 프로그램(PortAudio)이 자동으로 같이 깔립니다.**
> 윈도우에서는 따로 설치할 게 없습니다.

---

## 4단계 — 마이크 확인

```powershell
python list_audio_devices.py
```

마이크 목록이 나옵니다. **내장 마이크가 보이면 됩니다.**

아무것도 안 나오면 윈도우 설정에서 마이크 권한을 켜야 합니다.
설정 → 개인정보 보호 → 마이크 → **"앱이 마이크에 액세스하도록 허용"** 을 켜세요.

---

## 5단계 — 로봇 서버 켜기

**음성 명령은 로봇 쪽에서 서버가 돌고 있어야 작동합니다.**

PowerShell을 **새 창으로** 하나 더 열고, 로봇에 접속합니다.

```powershell
ssh stone0191@192.168.0.64
```

접속되면 아래를 **한 줄씩** 칩니다.

```bash
cd ~/ropi_robot
```

```bash
source venv/bin/activate
```

```bash
uvicorn raspberry_pi.ropi_robot_server:app --host 0.0.0.0 --port 8000
```

이런 글자가 나오면 서버가 켜진 겁니다.

```
Uvicorn running on http://0.0.0.0:8000
```

> **이 창은 닫지 마세요.** 닫으면 서버가 꺼집니다.
> 음성 명령을 쓰는 동안 계속 열어두세요.

> **`source venv/bin/activate` 를 빼먹으면 안 됩니다.**
> 서버는 켜지는데 로봇만 안 움직입니다. 원인을 찾기 아주 어려운 상태가 됩니다.

---

## 6단계 — 음성 AI 실행

**처음 열었던 PowerShell 창**(로봇에 접속하지 않은 창)으로 돌아옵니다.

### 로봇 주소와 API 키를 알려줍니다

```powershell
$env:ROPI_IP = "192.168.0.64"
```

```powershell
$env:OPENAI_API_KEY = "선생님께_받은_키"
```

> **이 두 줄은 PowerShell 창을 닫으면 사라집니다.** 새로 열면 다시 쳐야 합니다.
> 매번 치기 귀찮으면 아래 "매번 치지 않으려면"을 보세요.

### 실행

```powershell
cd ~\ropi-educational-ai-robot\laptop
```

```powershell
python ropi_voice_ai_client.py
```

**이제 마이크에 말하면 로봇이 움직입니다.**

---

## 이렇게 말하면 됩니다

| 말 | 로봇 동작 |
|---|---|
| "앞으로 가" / "전진" | 앞으로 |
| "뒤로 가" / "후진" | 뒤로 |
| "왼쪽으로 가" / "좌회전" | 왼쪽 |
| "오른쪽으로 가" / "우회전" | 오른쪽 |
| "멈춰" / "정지" / "스톱" | 멈추기 |

명령이 아닌 말을 하면 **AI가 대답합니다.** "안녕", "너 이름이 뭐야" 처럼 물어보세요.

---

## 매번 치지 않으려면

PowerShell 창을 닫아도 값이 남게 하는 방법입니다. **한 번만 하면 됩니다.**

```powershell
[Environment]::SetEnvironmentVariable("ROPI_IP", "192.168.0.64", "User")
```

```powershell
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "선생님께_받은_키", "User")
```

**설정한 뒤 PowerShell을 닫고 새로 열어야** 적용됩니다.

---

## 안 될 때

### "OPENAI_API_KEY가 없습니다"

```powershell
$env:OPENAI_API_KEY = "키"
```

를 안 쳤거나, PowerShell 창을 새로 열어서 사라진 겁니다.

### "키에 한글 등 ASCII가 아닌 문자가 있습니다"

**예시 문구를 그대로 붙여넣은 겁니다.** `선생님께_받은_키` 자리에 **진짜 키**를 넣어야 합니다.
진짜 키는 `sk-` 로 시작하고 50자가 넘습니다.

### "로봇 서버에 연결할 수 없습니다"

세 가지를 확인하세요.

1. **5단계 서버 창이 아직 열려 있나요?** 닫으면 꺼집니다.
2. **`$env:ROPI_IP` 가 내 로봇 주소인가요?**
3. **노트북과 로봇이 같은 와이파이인가요?**

이걸로 직접 확인할 수 있습니다.

```powershell
curl http://192.168.0.64:8000/status
```

글자가 나오면 서버는 살아 있습니다.

### 서버는 켜졌다는데 로봇이 안 움직여요

**서버 창에 이런 글자가 있는지 보세요.**

```
ModuleNotFoundError: No module named 'adafruit_servokit'
```

**`source venv/bin/activate` 를 빼먹은 겁니다.** 5단계를 처음부터 다시 하세요.

### 마이크가 안 잡혀요

```powershell
python list_audio_devices.py
```

목록이 비어 있으면 윈도우 마이크 권한을 켜세요.
설정 → 개인정보 보호 → 마이크

특정 마이크를 쓰고 싶으면 `ropi_voice_ai_client.py` 의 `MIC_DEVICE_INDEX` 에 번호를 넣습니다.

### 내 말을 잘 못 알아들어요

- **마이크에 가까이, 또박또박** 말하세요
- 주변이 시끄러우면 잘 안 됩니다
- 녹음 시간은 3초입니다. 짧게 말하세요

### 소리가 안 나와요

이어폰이 꽂혀 있는지, 윈도우 볼륨이 켜져 있는지 확인하세요.

---

## 선생님께

### API 키 관리

**학생들에게 키를 직접 나눠주면 유출됩니다.** 캠프가 끝나면 반드시 폐기하세요.

- 캠프 전용 키를 새로 발급하고, **사용 한도(Usage limit)를 낮게 걸어두세요**
- 캠프가 끝나면 <https://platform.openai.com/api-keys> 에서 삭제
- **학생이 키를 코드에 적어 커밋하는 사고를 막으려면** 환경변수만 쓰게 하세요.
  이 프로그램은 코드에 키를 넣을 수 없게 되어 있습니다.

### 미리 확인할 것

```powershell
# API 키가 실제로 쓸 수 있는지 (모델 3개를 검사합니다)
python check_openai.py
```

**세 개가 다 ✅ 여야 합니다.** 하나라도 ❌ 면 해당 기능이 안 됩니다.

- `gpt-4.1-mini` — 대화
- `gpt-4o-mini-tts` — 말하기
- `gpt-4o-mini-transcribe` — 듣기

### 서버를 자동으로 켜지게 하려면

지금은 로봇마다 SSH로 들어가서 서버를 켜야 합니다. **로봇 10대면 10번 해야 하고,
`source venv/bin/activate` 를 빼먹으면 원인 찾기 어려운 상태가 됩니다.**

부팅할 때 자동으로 켜지게 만들 수 있습니다. 필요하면 요청하세요.

### 시간 배분

**음성 AI는 키보드 조종보다 준비가 훨씬 많습니다.** 파이썬 설치, 패키지 설치,
마이크 권한, 서버 켜기, 환경변수 — 2시간 수업에 이걸 다 넣으면 조종할 시간이 없습니다.

**노트북에 미리 설치해두고 오시는 걸 권합니다.**
그러면 학생은 5단계(서버 켜기)와 6단계(실행)만 하면 됩니다.
