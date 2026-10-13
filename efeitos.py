import numpy as np
import sounddevice as sd

sd.default.device = "pulse"

TAXA = 44100
VOLUME = 0.3


def varredura(freq_inicial, freq_final, duracao):
    t = np.linspace(0, duracao, int(TAXA * duracao), endpoint=False)
    freq = freq_inicial * (freq_final / freq_inicial) ** (t / duracao)
    fase = 2 * np.pi * np.cumsum(freq) / TAXA
    onda = np.sin(fase) + 0.4 * np.sin(2 * fase)
    entrada = np.minimum(1, t / 0.02)
    saida = np.minimum(1, (duracao - t) / 0.12)
    return VOLUME * onda * entrada * saida / 1.4


def sino(freq, duracao):
    t = np.linspace(0, duracao, int(TAXA * duracao), endpoint=False)
    onda = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t)
    return VOLUME * 0.8 * onda * np.exp(-12 * t) / 1.3


SOM_ATIVAR = np.concatenate([varredura(400, 2200, 0.30), sino(1760, 0.30)]).astype(
    "float32"
)
SOM_DESATIVAR = varredura(1400, 300, 0.25).astype("float32")


def tocar(som):
    sd.play(som, TAXA)
    sd.wait()


def tocar_ativar():
    tocar(SOM_ATIVAR)


def tocar_desativar():
    tocar(SOM_DESATIVAR)


if __name__ == "__main__":
    print("Som de ativar...")
    tocar_ativar()
    print("Som de desativar...")
    tocar_desativar()
