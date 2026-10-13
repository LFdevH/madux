# =====================================================
#  voz.py — a voz da Madux
#  falar("texto") gera a fala com o Kokoro e toca na hora
# =====================================================
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf
from kokoro import KPipeline

VOZ = "pf_dora"        # voz feminina em português do Brasil
VELOCIDADE = 0.95      # 1.0 = normal, menor = mais calma
EFEITO = "highpass=f=120,aecho=0.8:0.6:25:0.2,treble=g=3,loudnorm=I=-14:TP=-1"
ARQUIVO_STATUS = Path.home() / ".cache/madux/status"

print("[voz] carregando o Kokoro...")
_pipeline = KPipeline(lang_code="p")   # "p" = português do Brasil


def mudar_status(estado):
    """Avisa a barra do Qtile: online, ouvindo, falando ou offline."""
    ARQUIVO_STATUS.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO_STATUS.write_text(estado)


def achar_saida():
    """Prefere tocar pelo PipeWire (o mesmo som do sistema)."""
    for preferido in ("pipewire", "pulse", "default"):
        for numero, disp in enumerate(sd.query_devices()):
            if disp["name"] == preferido and disp["max_output_channels"] > 0:
                return numero
    return None


SAIDA = achar_saida()


def falar(texto):
    # 1. texto -> som cru (o Kokoro devolve em pedaços)
    pedacos = [np.asarray(a) for _, _, a in _pipeline(texto, voice=VOZ, speed=VELOCIDADE)
               if a is not None]
    cru = np.concatenate(pedacos)

    # 2. efeito de IA com o ffmpeg (numa pasta temporária que some sozinha)
    with tempfile.TemporaryDirectory() as pasta:
        entrada = Path(pasta) / "cru.wav"
        saida = Path(pasta) / "pronto.wav"
        sf.write(entrada, cru, 24000)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(entrada),
                        "-af", EFEITO, "-ar", "48000", str(saida)], check=True)
        som, taxa = sf.read(saida, dtype="float32")

    # 3. toca, avisando a barra
    mudar_status("falando")
    sd.play(som, taxa, device=SAIDA)
    sd.wait()
    mudar_status("online")


# só roda quando você executa "python voz.py" direto
if __name__ == "__main__":
    falar("Oi, éle éfe. Agora eu consigo falar na hora.")
