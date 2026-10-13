import glob

import numpy as np
import sounddevice as sd
from resemblyzer import VoiceEncoder, preprocess_wav

sd.default.device = "pulse"
encoder = VoiceEncoder()

vozes = {}
for arquivo in glob.glob("voz_*.npy"):
    nome = arquivo[4:-4]
    vozes[nome] = np.load(arquivo)

print("Vozes cadastradas:", list(vozes.keys()))

while True:
    input("Aperta Enter e fala (Ctrl+C pra sair)...")
    audio = sd.rec(3 * 16000, samplerate=16000, channels=1, dtype="float32")
    sd.wait()
    limpo = preprocess_wav(audio.flatten(), source_sr=16000)
    vetor = encoder.embed_utterance(limpo)

    for nome in vozes:
        similaridade = np.dot(vetor, vozes[nome])
        print("  parecido com", nome, ":", round(float(similaridade), 3))
