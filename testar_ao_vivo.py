from ouvido import ouvir_audio
from quem import nota_maria

print("Teste ao vivo. Ctrl+C pra sair.")

while True:
    texto, audio = ouvir_audio("Fala...")
    nota = nota_maria(audio)
    print("Ouvi:", repr(texto), "| Nota Maria:", round(nota, 3))
