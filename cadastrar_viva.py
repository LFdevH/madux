import shutil
import sys

import numpy as np
from resemblyzer import preprocess_wav

from ouvido import ouvir_audio
from quem import encoder

# Frases para a pessoa falar de forma NATURAL (não precisa ser igual, é só ideia).
FRASES = [
    "Madux, que horas são?",
    "Madux, me conta uma curiosidade.",
    "Madux, como foi o seu dia?",
    "Madux!",
    "Madux, o que você aprendeu hoje?",
    "Madux, me fala uma piada.",
    "Madux, tô com fome, o que eu como?",
    "Madux, você tá me ouvindo?",
    "Madux, quem é a rainha aqui?",
    "Madux, me ajuda com uma coisa.",
    "Madux.",
    "Madux, o LF tá te ensinando direitinho?",
]

nome = sys.argv[1] if len(sys.argv) > 1 else "maria"
arquivo = f"voz_{nome}.npy"

# Guarda uma cópia da digital antiga, por segurança
try:
    shutil.copy(arquivo, f"voz_{nome}_antiga.npy")
    print(f"(copia da digital antiga salva em voz_{nome}_antiga.npy)")
except FileNotFoundError:
    pass

print(f"\nCadastro AO VIVO de: {nome}")
print("Fale cada frase do jeito que falaria no dia a dia.")
print("Varie: perto, um pouco longe, rindo, sério, brincando.\n")

embeddings = []

for frase in FRASES:
    print(f"\nSugestão: {frase}")
    input("Aperte Enter e fale... ")
    texto, audio = ouvir_audio("Pode falar...")

    if audio is None:
        print("  Não ouvi nada, essa foi pulada.")
        continue

    limpo = preprocess_wav(np.asarray(audio, dtype=np.float32).flatten())
    if len(limpo) < 4000:
        print("  Muito curto, essa foi pulada.")
        continue

    embeddings.append(encoder.embed_utterance(limpo))
    print(f"  OK! Whisper ouviu: {texto!r}")

if len(embeddings) < 6:
    print("\nPoucas amostras boas. Rode de novo e nada foi salvo.")
    sys.exit()

media = np.mean(embeddings, axis=0)
media = media / np.linalg.norm(media)
np.save(arquivo, media)
print(f"\nPronto! {len(embeddings)} amostras. Salvo em {arquivo}")
