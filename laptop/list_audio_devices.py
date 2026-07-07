import sounddevice as sd

print(sd.query_devices())
print()
print("현재 기본 장치:", sd.default.device)
