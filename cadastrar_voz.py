import sys

import numpy as np
import sounddevice as sd
from resemblyzer import VoiceEncoder, preprocess_wav

sd.default.device = "pulse"

GRAVACOES = 8
SEGUNDOS = 3

nome = sys.argv[1]
encoder = VoiceEncoder()
vetores = []

print("Vou gravar", GRAVACOES, "vezes. Em cada uma, fala 'Madux' e uma frase curta.")

for i in range(GRAVACOES):
    input("Gravação " + str(i + 1) + "/" + str(GRAVACOES) + ": aperta Enter e fala...")
    audio = sd.rec(SEGUNDOS * 16000, samplerate=16000, channels=1, dtype="float32")
    sd.wait()
    limpo = preprocess_wav(audio.flatten(), source_sr=16000)
    vetores.append(encoder.embed_utterance(limpo))

voz = np.mean(vetores, axis=0)
voz = voz / np.linalg.norm(voz)
np.save("voz_" + nome + ".npy", voz)
print("Salvo em voz_" + nome + ".npy")
