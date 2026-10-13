# =====================================================
#  ouvir.py — os ouvidos da Madux
#  ouvir_frase() espera você falar, grava até você parar
#  e devolve o texto
# =====================================================
import collections

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

TAXA_WHISPER = 16000   # o Whisper trabalha com 16 mil amostras por segundo
BLOCO_SEG = 0.1        # analisa o som em pedaços de 0,1 segundo
SILENCIO_FIM = 0.9     # 0,9 s de silêncio = você terminou de falar
MAXIMO_SEG = 10        # frase mais longa que ela aceita


def achar_microfone():
    """Prefere o microfone pelo PipeWire (o mesmo que o sistema usa)."""
    for preferido in ("pipewire", "pulse", "default"):
        for numero, disp in enumerate(sd.query_devices()):
            if disp["name"] == preferido and disp["max_input_channels"] > 0:
                return numero
    return None


MIC = achar_microfone()
TAXA_MIC = int(sd.query_devices(MIC, kind="input")["default_samplerate"])
BLOCO = int(TAXA_MIC * BLOCO_SEG)
LIMIAR = None          # volume que separa "voz" de "barulho de fundo"

print("[ouvir] carregando o Whisper...")
_modelo = WhisperModel("small", device="cpu", compute_type="int8")


def volume(bloco):
    """Volume médio do bloco (raiz da média dos quadrados)."""
    return float(np.sqrt(np.mean(bloco ** 2)))


def calibrar(stream, segundos=1.0):
    """Mede o barulho de fundo do lugar. Fica em silêncio nesse 1 segundo!"""
    blocos = [stream.read(BLOCO)[0][:, 0] for _ in range(int(segundos / BLOCO_SEG))]
    ruido = float(np.mean([volume(b) for b in blocos]))
    return max(ruido * 3, 0.01)


def converter_taxa(audio):
    """Da taxa do microfone (48 mil) pra taxa do Whisper (16 mil)."""
    tamanho_novo = int(len(audio) * TAXA_WHISPER / TAXA_MIC)
    posicoes = np.linspace(0, len(audio), tamanho_novo, endpoint=False)
    return np.interp(posicoes, np.arange(len(audio)), audio).astype(np.float32)


def gravar_frase():
    global LIMIAR
    with sd.InputStream(samplerate=TAXA_MIC, channels=1, dtype="float32",
                        device=MIC, blocksize=BLOCO) as stream:
        if LIMIAR is None:
            LIMIAR = calibrar(stream)
            print(f"[ouvir] limiar de voz: {LIMIAR:.4f}")

        antes = collections.deque(maxlen=3)   # guarda 0,3 s de antes da fala
        frase = []
        silencio = 0.0

        while True:
            bloco = stream.read(BLOCO)[0][:, 0].copy()
            tem_voz = volume(bloco) > LIMIAR

            if not frase:                     # ainda esperando você começar
                antes.append(bloco)
                if tem_voz:
                    frase = list(antes)       # começou! inclui o pedacinho de antes
                continue

            frase.append(bloco)
            silencio = 0.0 if tem_voz else silencio + BLOCO_SEG
            if silencio >= SILENCIO_FIM or len(frase) * BLOCO_SEG >= MAXIMO_SEG:
                break

    return converter_taxa(np.concatenate(frase))


def transcrever(audio):
    trechos, _ = _modelo.transcribe(
        audio,
        language="pt",
        initial_prompt="Madux, que horas são?",   # ensina como se escreve o nome dela
        vad_filter=True,                           # ignora pedaços sem voz
    )
    return " ".join(t.text.strip() for t in trechos).strip()


def ouvir_frase():
    return transcrever(gravar_frase())


# teste: "python ouvir.py" fica mostrando tudo o que ouve
if __name__ == "__main__":
    print("fala alguma coisa (Ctrl+C sai)")
    while True:
        print("ouvi:", ouvir_frase() or "(nada)")
