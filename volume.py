import numpy as np
import sounddevice as sd

sd.default.device = "pulse"

with sd.InputStream(samplerate=16000, channels=1, dtype="float32") as microfone:
    for i in range(50):
        pedaco, _ = microfone.read(1600)
        volume = np.abs(pedaco).mean()
        print(round(volume, 4))
