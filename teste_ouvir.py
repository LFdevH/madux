# teste_ouvir.py — grava 5 segundos do microfone e mostra o texto

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

TAXA_WHISPER = 16000   # o Whisper trabalha com 16 mil amostras por segundo
SEGUNDOS = 5


def achar_microfone():
    """Prefere o microfone pelo PipeWire (o mesmo que o sistema usa).
    Se não achar, cai no padrão."""
    for preferido in ("pipewire", "pulse", "default"):
        for numero, disp in enumerate(sd.query_devices()):
            if disp["name"] == preferido and disp["max_input_channels"] > 0:
                return numero
    return None   # None = deixa o sounddevice escolher


MIC = achar_microfone()
info_mic = sd.query_devices(MIC, kind="input")
TAXA_MIC = int(info_mic["default_samplerate"])
print(f"microfone: {info_mic['name']} ({TAXA_MIC} amostras/s)")

print("carregando o modelo...")
modelo = WhisperModel("small", device="cpu", compute_type="int8")

print(f"fala alguma coisa! gravando {SEGUNDOS} segundos...")
audio = sd.rec(SEGUNDOS * TAXA_MIC, samplerate=TAXA_MIC, channels=1,
               dtype="float32", device=MIC)
sd.wait()              # espera terminar de gravar
audio = audio[:, 0]    # só o canal 0 (mono)

# medidor: o som vai de -1 a 1; perto de 0 = silêncio
volume = float(np.abs(audio).max())
print(f"volume máximo: {volume:.3f}", "(silêncio!)" if volume < 0.01 else "(ok)")

# converte da taxa do microfone pra taxa do Whisper
tamanho_novo = int(len(audio) * TAXA_WHISPER / TAXA_MIC)
posicoes = np.linspace(0, len(audio), tamanho_novo, endpoint=False)
audio = np.interp(posicoes, np.arange(len(audio)), audio).astype(np.float32)

print("pronto, transcrevendo...")
trechos, info = modelo.transcribe(audio, language="pt")
texto = " ".join(t.text.strip() for t in trechos)

print("você disse:", texto if texto else "(nada)")
