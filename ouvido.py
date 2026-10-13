import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from faster_whisper.vad import VadOptions, get_speech_timestamps

sd.default.device = "pulse"
modelo = WhisperModel("small", device="cpu", compute_type="int8")

OPCOES_VAD = VadOptions(min_speech_duration_ms=150)
JANELA = 5
PAUSA = 5
MAXIMO = 150
VOCABULARIO = "Conversa com a Madux. O usuário se chama LF."


def tem_voz(audio):
    trechos = get_speech_timestamps(audio, OPCOES_VAD)
    return len(trechos) > 0


def ouvir_audio(aviso="Fala alguma coisa...", processo=None):
    pedacos = []
    silencio = 0
    falou = False

    with sd.InputStream(samplerate=16000, channels=1, dtype="float32") as microfone:
        microfone.read(1600)
        print(aviso)

        while True:
            if processo is not None and processo.poll() is not None:
                break

            pedaco, _ = microfone.read(1600)
            pedacos.append(pedaco)

            if len(pedacos) >= JANELA:
                janela = np.concatenate(pedacos[-JANELA:]).flatten()
                if tem_voz(janela):
                    falou = True
                    silencio = 0
                else:
                    silencio = silencio + 1

            if falou and silencio >= PAUSA:
                break
            if len(pedacos) >= MAXIMO:
                break

    if not falou:
        return "", None

    audio = np.concatenate(pedacos).flatten()
    partes, _ = modelo.transcribe(
        audio,
        language="pt",
        vad_filter=True,
        initial_prompt=VOCABULARIO,
    )

    texto = ""
    for parte in partes:
        texto = texto + parte.text
    return texto.strip(), audio


def ouvir(aviso="Fala alguma coisa...", processo=None):
    texto, _ = ouvir_audio(aviso, processo)
    return texto
