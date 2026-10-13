import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav

LIMITE_ENTRAR = 0.74
LIMITE_SAIR = 0.70

encoder = VoiceEncoder()
voz_maria = np.load("voz_maria.npy")


def nota_maria(audio):
    if audio is None:
        return 0.0
    limpo = preprocess_wav(audio, source_sr=16000)
    if len(limpo) < 4000:
        return 0.0
    vetor = encoder.embed_utterance(limpo)
    return float(np.dot(vetor, voz_maria))


def decidir_modo(rainha, nota):
    if nota >= LIMITE_ENTRAR:
        return True
    if nota < LIMITE_SAIR:
        return False
    return rainha
