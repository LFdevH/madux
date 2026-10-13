# =====================================================
#  madux.py — a Madux (programa principal)
#  Fica ouvindo; quando você fala "Madux ...", ela responde.
# =====================================================
import datetime
import difflib
import re
import subprocess
import unicodedata

from voz import falar, mudar_status
from ouvir import ouvir_frase

NOME = "madux"

DIAS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
        "sexta-feira", "sábado", "domingo"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]

#  palavra que você fala  ->  (comando que roda, nome que ela fala)
PROGRAMAS = {
    "firefox":   ("firefox", "o Firefox"),
    "navegador": ("firefox", "o navegador"),
    "terminal":  ("alacritty", "o terminal"),
    "spotify":   ("spotify", "o Spotify"),
    "codigo":    ("code", "o VS Code"),
}


# ---------- 1. ENTENDER O TEXTO ----------
def normalizar(texto):
    """'Madux, que horas são?' -> ['madux', 'que', 'horas', 'sao']"""
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")  # tira acentos
    return re.sub(r"[^a-z0-9 ]", " ", texto).split()                       # tira pontuação


def separar_chamado(palavras):
    """Procura o nome dela no que você disse, aceitando erros do Whisper
    (madox, maduxe, mad ux...). Devolve as palavras DEPOIS do nome,
    ou None se ninguém chamou a Madux."""
    for i in range(len(palavras)):
        # testa a palavra sozinha e grudada na próxima ("mad" + "ux")
        candidatos = [(palavras[i], 1)]
        if i + 1 < len(palavras):
            candidatos.append((palavras[i] + palavras[i + 1], 2))
        # fica com o candidato mais parecido com "madux"
        notas = [(difflib.SequenceMatcher(None, c, NOME).ratio(), usadas)
                 for c, usadas in candidatos]
        nota, usadas = max(notas)
        if nota >= 0.75:
            return palavras[i + usadas:]
    return None


# ---------- 2. RESPOSTAS ----------
def dizer_hora(agora):
    h, m = agora.hour, agora.minute
    inicio = "É uma hora" if h == 1 else f"São {h} horas"
    if m == 0:
        return f"{inicio} em ponto."
    return f"{inicio} e {m} minuto{'s' if m > 1 else ''}."


def responder(palavras):
    """Executa o pedido. Devolve False quando é pra desligar."""
    frase = " ".join(palavras)
    agora = datetime.datetime.now()

    if any(p in frase for p in ("desliga", "tchau", "dormir")):
        falar("Até mais, éle éfe.")
        return False

    if any(p in frase for p in ("bom dia", "boa tarde", "boa noite")) or "oi" in palavras:
        falar("Oi, éle éfe. Tô aqui.")
    elif "hora" in frase:                              # "hora", "horas"
        falar(dizer_hora(agora))
    elif "dia" in palavras or "data" in palavras or "hoje" in palavras:
        falar(f"Hoje é {DIAS[agora.weekday()]}, {agora.day} de {MESES[agora.month - 1]}.")
    elif any(p.startswith("abr") for p in palavras):   # "abre", "abrir", "abra"
        for palavra, (comando, nome) in PROGRAMAS.items():
            if palavra in palavras:
                subprocess.Popen([comando])
                falar(f"Abrindo {nome}.")
                break
        else:
            falar("Não sei abrir esse programa ainda.")
    elif "nome" in palavras or "quem" in palavras:
        falar("Eu sou a Madux, a assistente do éle éfe. "
              "Meu nome vem de um apelido da Maria Eduarda.")
    else:
        falar("Ainda não sei fazer isso. Meu cérebro de verdade chega na próxima etapa.")
    return True


# ---------- 3. O LOOP PRINCIPAL ----------
def main():
    falar("Madux online.")
    try:
        while True:
            texto = ouvir_frase()
            if not texto:
                continue
            print(f"[ouvi] {texto}")

            pedido = separar_chamado(normalizar(texto))
            if pedido is None:              # falou, mas não chamou a Madux
                continue

            mudar_status("ouvindo")
            if not pedido:                  # disse só "Madux"
                falar("Sim?")
                mudar_status("ouvindo")
                texto = ouvir_frase()
                print(f"[ouvi] {texto}")
                pedido = normalizar(texto)

            if not responder(pedido):
                break
            mudar_status("online")
    except KeyboardInterrupt:
        pass
    finally:
        mudar_status("offline")


if __name__ == "__main__":
    main()
