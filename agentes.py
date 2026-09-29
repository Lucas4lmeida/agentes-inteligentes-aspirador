"""Aspirador reativo simples e aspirador reativo baseado em modelo.

Sensores: sujeira no quadrado atual e direcoes vizinhas livres.
Os agentes nao recebem o mapa, o tamanho nem a sujeira dos vizinhos.
Cada acao ocupa um periodo. Nao aparece sujeira nova.
Pontos 1: soma dos quadrados limpos ao fim de cada periodo.
Pontos 2: Pontos 1 menos a quantidade de movimentos.
Obstaculos nao contam como quadrados limpos.

Execute:
    python3 agentes.py
    python3 agentes.py --replay
    python3 agentes.py --replay --cenario 2 --atraso 0.25
"""

import argparse
import csv
import json
import random
import statistics
import sys
import time
from collections import deque
from pathlib import Path


# CONFIGURACOES: altere estes valores para fazer outros testes.
SEMENTE = 42  # Repete o sorteio do agente simples e os cenarios aleatorios.
PASSOS = 80  # Total de acoes por execucao, incluindo aspirar.
TAMANHO = 4  # Quantidade de linhas e colunas da grade.
CENARIOS_ALEATORIOS = 30
SEMENTES_SIMPLES = 5  # O agente simples repete cada cenario aleatorio.

# Cada cenario: sujeira inicial, obstaculos, posicao inicial.
# Posicoes usam (linha, coluna), de 0 ate TAMANHO - 1.
CENARIOS = [
    ({(0, 0), (0, 3), (3, 0), (3, 3)}, set(), (0, 0)),
    ({(0, 2), (1, 3), (2, 0), (3, 2)}, {(1, 1), (2, 1)}, (3, 0)),
    ({(0, 0), (1, 0), (2, 2), (3, 3)}, {(1, 2), (2, 1)}, (0, 3)),
]

# Regras fixas: direita, baixo, esquerda e cima.
DIRECOES = ((0, 1), (1, 0), (0, -1), (-1, 0))
NOME_DIRECAO = {
    (0, 1): "direita",
    (1, 0): "baixo",
    (0, -1): "esquerda",
    (-1, 0): "cima",
}
ASPIRAR = "aspirar"
PARAR = "parar"
PASTA = Path(__file__).resolve().parent
COR_SIMPLES = "#2f6fad"
COR_MEMORIA = "#1f8a5b"


class ReativoSimples:
    """Reativo simples: a decisao usa so o percepto atual."""

    def __init__(self, semente=SEMENTE):
        self.sorteio = random.Random(semente)

    def agir(self, sujo, caminhos):
        if sujo:
            return ASPIRAR
        if caminhos:
            return self.sorteio.choice(caminhos)
        return PARAR


class ReativoComMemoria:
    """Reativo baseado em modelo.

    O estado fica em coordenadas relativas ao inicio. Guarda se cada
    celula conhecida esta limpa, bloqueada ou ainda nao visitada, e
    quantas vezes foi visitada. A sujeira distante nao aparece no
    sensor: ela so entra no estado quando o agente esta sobre ela.
    """

    def __init__(self):
        self.posicao = (0, 0)
        self.visitas = {}
        self.estado = {}

    def incorporar(self, sujo, caminhos):
        self.estado[self.posicao] = "sujo" if sujo else "limpo"
        self.visitas[self.posicao] = self.visitas.get(self.posicao, 0) + 1
        livres = set(caminhos)
        for direcao in DIRECOES:
            vizinho = (self.posicao[0] + direcao[0], self.posicao[1] + direcao[1])
            if direcao in livres:
                if self.estado.get(vizinho) not in ("limpo", "sujo"):
                    self.estado[vizinho] = "desconhecido"
            elif self.estado.get(vizinho) not in ("limpo", "sujo"):
                self.estado[vizinho] = "bloqueado"

    def decidir(self):
        if self.estado.get(self.posicao) == "sujo":
            return ASPIRAR
        passo = self._passo_ate_trabalho()
        if passo is None:
            return PARAR
        return passo

    def aplicar(self, acao):
        # O sensor ja garantiu a passagem e o mundo e deterministico.
        if acao == ASPIRAR:
            self.estado[self.posicao] = "limpo"
        elif acao != PARAR:
            self.posicao = (self.posicao[0] + acao[0], self.posicao[1] + acao[1])

    def agir(self, sujo, caminhos):
        self.incorporar(sujo, caminhos)
        acao = self.decidir()
        self.aplicar(acao)
        return acao

    def _passo_ate_trabalho(self):
        inicio = self.posicao
        fila = deque([inicio])
        distancia = {inicio: 0}
        pai = {inicio: None}
        while fila:
            celula = fila.popleft()
            opcoes = []
            for indice, direcao in enumerate(DIRECOES):
                vizinho = (celula[0] + direcao[0], celula[1] + direcao[1])
                if vizinho in distancia:
                    continue
                if self.estado.get(vizinho) in ("limpo", "sujo", "desconhecido"):
                    opcoes.append((self.visitas.get(vizinho, 0), indice, vizinho))
            for _, _, vizinho in sorted(opcoes):
                distancia[vizinho] = distancia[celula] + 1
                pai[vizinho] = celula
                fila.append(vizinho)

        candidatos = [
            celula
            for celula, estado in self.estado.items()
            if estado in ("sujo", "desconhecido") and celula in distancia and celula != inicio
        ]
        if not candidatos:
            return None
        menor = min(distancia[celula] for celula in candidatos)
        proximos = [celula for celula in candidatos if distancia[celula] == menor]

        def chave(alvo):
            celula = alvo
            while pai[celula] != inicio:
                celula = pai[celula]
            direcao = (celula[0] - inicio[0], celula[1] - inicio[1])
            return (self.visitas.get(celula, 0), DIRECOES.index(direcao))

        alvo = min(proximos, key=chave)
        celula = alvo
        while pai[celula] != inicio:
            celula = pai[celula]
        return (celula[0] - inicio[0], celula[1] - inicio[1])


def nome_acao(acao):
    if acao in NOME_DIRECAO:
        return NOME_DIRECAO[acao]
    return acao


def celulas_alcancaveis(inicio, obstaculos, tamanho=TAMANHO):
    vistos = set()
    fila = [inicio]
    while fila:
        atual = fila.pop()
        if atual in vistos:
            continue
        vistos.add(atual)
        for dl, dc in DIRECOES:
            vizinho = (atual[0] + dl, atual[1] + dc)
            if (
                0 <= vizinho[0] < tamanho
                and 0 <= vizinho[1] < tamanho
                and vizinho not in obstaculos
                and vizinho not in vistos
            ):
                fila.append(vizinho)
    return vistos


def caminhos_livres(posicao, obstaculos, tamanho=TAMANHO):
    linha, coluna = posicao
    caminhos = []
    for dl, dc in DIRECOES:
        vizinho = (linha + dl, coluna + dc)
        if (
            0 <= vizinho[0] < tamanho
            and 0 <= vizinho[1] < tamanho
            and vizinho not in obstaculos
        ):
            caminhos.append((dl, dc))
    return caminhos


def modelo_absoluto(agente, inicio, tamanho=TAMANHO):
    if not isinstance(agente, ReativoComMemoria):
        return None
    celulas = []
    for (linha, coluna), estado in agente.estado.items():
        absoluta = (inicio[0] + linha, inicio[1] + coluna)
        if 0 <= absoluta[0] < tamanho and 0 <= absoluta[1] < tamanho:
            celulas.append(
                {
                    "l": absoluta[0],
                    "c": absoluta[1],
                    "estado": estado,
                    "visitas": agente.visitas.get((linha, coluna), 0),
                }
            )
    celulas.sort(key=lambda item: (item["l"], item["c"]))
    relativa = agente.posicao
    return {
        "pos": [inicio[0] + relativa[0], inicio[1] + relativa[1]],
        "celulas": celulas,
    }


def quadro(posicao, sujeira, acao, movimentos, pontos, modelo):
    return {
        "pos": [posicao[0], posicao[1]],
        "sujeira": [[linha, coluna] for linha, coluna in sorted(sujeira)],
        "acao": acao,
        "mov": movimentos,
        "p1": pontos,
        "p2": pontos - movimentos,
        "modelo": modelo,
    }


def simular(agente, sujeira_inicial, obstaculos, inicio, periodos=PASSOS, registrar=False):
    if TAMANHO < 1 or periodos < 1:
        raise ValueError("TAMANHO e PASSOS devem ser maiores que zero.")
    posicoes = set(sujeira_inicial) | set(obstaculos) | {inicio}
    if any(not (0 <= linha < TAMANHO and 0 <= coluna < TAMANHO) for linha, coluna in posicoes):
        raise ValueError("Ha posicoes fora do TAMANHO da grade.")
    if inicio in obstaculos or set(sujeira_inicial) & set(obstaculos):
        raise ValueError("O inicio e a sujeira nao podem ficar em obstaculos.")

    sujeira = set(sujeira_inicial)
    obstaculos = set(obstaculos)
    posicao = inicio
    movimentos = 0
    pontos = 0
    acoes = []
    quadrados_livres = TAMANHO * TAMANHO - len(obstaculos)
    frames = []
    if registrar:
        modelo = {"pos": None, "celulas": []} if isinstance(agente, ReativoComMemoria) else None
        frames.append(quadro(posicao, sujeira, "inicio", 0, 0, modelo))

    for _ in range(periodos):
        acao = agente.agir(posicao in sujeira, caminhos_livres(posicao, obstaculos))
        acoes.append(acao)
        if acao == ASPIRAR:
            sujeira.discard(posicao)
        elif acao != PARAR:
            posicao = (posicao[0] + acao[0], posicao[1] + acao[1])
            movimentos += 1
        pontos += quadrados_livres - len(sujeira)
        if registrar:
            frames.append(
                quadro(
                    posicao,
                    sujeira,
                    nome_acao(acao),
                    movimentos,
                    pontos,
                    modelo_absoluto(agente, inicio),
                )
            )

    parou = None
    if acoes and acoes[-1] == PARAR:
        indice = len(acoes) - 1
        while indice >= 0 and acoes[indice] == PARAR:
            indice -= 1
        parou = indice + 2
    alcancavel = len(sujeira & celulas_alcancaveis(inicio, obstaculos))
    return {
        "sujeira": len(sujeira),
        "alcancavel": alcancavel,
        "movimentos": movimentos,
        "parou": parou,
        "p1": pontos,
        "p2": pontos - movimentos,
        "frames": frames,
    }


def gerar_cenarios(quantidade, semente, tamanho=TAMANHO, max_obstaculos=2):
    if tamanho < 1 or max_obstaculos < 0:
        raise ValueError("O tamanho deve ser positivo e max_obstaculos nao pode ser negativo.")
    sorteio = random.Random(semente)
    todas = [(linha, coluna) for linha in range(tamanho) for coluna in range(tamanho)]
    # Reserva pelo menos uma celula livre para a posicao inicial.
    limite_obstaculos = min(max_obstaculos, len(todas) - 1)
    cenarios = []
    for _ in range(quantidade):
        n_obstaculos = sorteio.randint(0, limite_obstaculos)
        obstaculos = set(sorteio.sample(todas, n_obstaculos))
        livres = [posicao for posicao in todas if posicao not in obstaculos]
        teto = min(5, len(livres))
        piso = min(2, teto)
        sujeira = set(sorteio.sample(livres, sorteio.randint(piso, teto)))
        inicio = sorteio.choice(livres)
        cenarios.append((sujeira, obstaculos, inicio))
    return cenarios


def serializar_posicoes(posicoes):
    return " ".join(f"{linha},{coluna}" for linha, coluna in sorted(posicoes))


def texto_parou(parou):
    if parou is None:
        return "-"
    return str(parou)


def dispersao(valores):
    if len(valores) < 2:
        return 0.0
    return statistics.stdev(valores)


def imprimir_fixos(resultados):
    print(f"Ambiente: {TAMANHO}x{TAMANHO} | Periodos: {resultados[0]['passos']}")
    print("Pontos 1: limpeza acumulada | Pontos 2: Pontos 1 - movimentos")
    print(f"O agente simples usa a semente {SEMENTE}.")
    print("O agente com memoria para quando o mapa conhecido esta limpo.")
    print("Alc. = sujeira restante ainda alcancavel. Parou = periodo em que a parada comecou.\n")
    print(
        f"{'Cenario':<8}{'Agente':<14}{'Sujeira':>8}{'Alc.':>6}"
        f"{'Mov.':>6}{'Parou':>7}{'Pontos 1':>10}{'Pontos 2':>10}"
    )
    for item in resultados:
        print(
            f"{item['cenario']:<8}{item['agente']:<14}{item['sujeira']:>8}"
            f"{item['alcancavel']:>6}{item['movimentos']:>6}{texto_parou(item['parou']):>7}"
            f"{item['p1']:>10}{item['p2']:>10}"
        )

    print(f"\nMedia das pontuacoes nos {len(CENARIOS)} cenarios fixos:")
    for nome in ("Simples", "Com memoria"):
        grupo = [item for item in resultados if item["agente"] == nome]
        p1 = statistics.mean(item["p1"] for item in grupo)
        p2 = statistics.mean(item["p2"] for item in grupo)
        print(f"{nome}: Pontos 1 = {p1:.2f} | Pontos 2 = {p2:.2f}")


def avaliar_aleatorios(cenarios, sementes, passos):
    linhas = []
    detalhes = []
    for numero, (sujeira, obstaculos, inicio) in enumerate(cenarios, 1):
        simples = []
        for semente in sementes:
            resultado = simular(ReativoSimples(semente), sujeira, obstaculos, inicio, passos)
            simples.append(resultado)
            detalhes.append((numero, semente, "Simples", sujeira, obstaculos, inicio, resultado))
        memoria = simular(ReativoComMemoria(), sujeira, obstaculos, inicio, passos)
        detalhes.append((numero, "", "Com memoria", sujeira, obstaculos, inicio, memoria))
        linhas.append(
            {
                "cenario": numero,
                "simples_p1": statistics.mean(item["p1"] for item in simples),
                "simples_p2": statistics.mean(item["p2"] for item in simples),
                "simples_mov": statistics.mean(item["movimentos"] for item in simples),
                "simples_alc": statistics.mean(item["alcancavel"] for item in simples),
                "memoria_p1": memoria["p1"],
                "memoria_p2": memoria["p2"],
                "memoria_mov": memoria["movimentos"],
                "memoria_parou": memoria["parou"],
                "memoria_alc": memoria["alcancavel"],
                "simples_limpos": sum(item["alcancavel"] == 0 for item in simples),
                "execucoes": len(simples),
            }
        )
    return linhas, detalhes


def imprimir_aleatorios(linhas, sementes):
    print(
        f"\nCenarios aleatorios: {len(linhas)} | grade fixa {TAMANHO}x{TAMANHO} | "
        f"sujeira, obstaculos e inicio variam"
    )
    print(
        "Cada linha do agente simples e a media das sementes "
        + ", ".join(str(semente) for semente in sementes)
        + "."
    )
    print(
        f"{'#':>3} {'Simples P1':>10} {'Simples P2':>10} {'Memoria P1':>10} "
        f"{'Memoria P2':>10} {'Parou':>6} {'Mov.S':>7} {'Mov.M':>6} {'Alc.M':>6}"
    )
    for item in linhas:
        print(
            f"{item['cenario']:>3} {item['simples_p1']:10.1f} {item['simples_p2']:10.1f} "
            f"{item['memoria_p1']:10.0f} {item['memoria_p2']:10.0f} "
            f"{texto_parou(item['memoria_parou']):>6} {item['simples_mov']:7.1f} "
            f"{item['memoria_mov']:6.0f} {item['memoria_alc']:6.0f}"
        )

    def bloco(titulo, p1, p2):
        cabeca = f"{titulo}: "
        print(
            f"{cabeca}Pontos 1 = {statistics.mean(p1):.2f} "
            f"(desvio {dispersao(p1):.2f}, min {min(p1):.0f}, max {max(p1):.0f})"
        )
        print(
            f"{' ' * len(cabeca)}Pontos 2 = {statistics.mean(p2):.2f} "
            f"(desvio {dispersao(p2):.2f}, min {min(p2):.0f}, max {max(p2):.0f})"
        )

    print(f"\nMedia global nos {len(linhas)} cenarios aleatorios:")
    bloco(
        "Simples",
        [item["simples_p1"] for item in linhas],
        [item["simples_p2"] for item in linhas],
    )
    bloco(
        "Com memoria",
        [item["memoria_p1"] for item in linhas],
        [item["memoria_p2"] for item in linhas],
    )
    frente = sum(item["memoria_p2"] > item["simples_p2"] for item in linhas)
    empates = sum(item["memoria_p2"] == item["simples_p2"] for item in linhas)
    limpos = sum(item["simples_limpos"] for item in linhas)
    execucoes = sum(item["execucoes"] for item in linhas)
    memoria_limpa = sum(item["memoria_alc"] == 0 for item in linhas)
    print(
        f"Pontos 2 maior para o agente com memoria em {frente} de {len(linhas)} cenarios"
        + (f" ({empates} empates)." if empates else ".")
    )
    print(
        f"Sujeira alcancavel removida: simples em {limpos} de {execucoes} execucoes; "
        f"com memoria em {memoria_limpa} de {len(linhas)} cenarios."
    )


def salvar_csv(caminho, fixos, detalhes, passos):
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(
            [
                "tipo",
                "cenario",
                "semente",
                "agente",
                "sujeira",
                "obstaculos",
                "inicio",
                "sujeira_final",
                "alcancavel",
                "movimentos",
                "parou",
                "pontos1",
                "pontos2",
                "passos",
                "tamanho",
            ]
        )
        for item in fixos:
            escritor.writerow(
                [
                    "fixo",
                    item["cenario"],
                    item["semente"],
                    item["agente"],
                    serializar_posicoes(item["sujeira_inicial"]),
                    serializar_posicoes(item["obstaculos"]),
                    serializar_posicoes([item["inicio"]]),
                    item["sujeira"],
                    item["alcancavel"],
                    item["movimentos"],
                    texto_parou(item["parou"]),
                    item["p1"],
                    item["p2"],
                    passos,
                    TAMANHO,
                ]
            )
        for numero, semente, agente, sujeira, obstaculos, inicio, resultado in detalhes:
            escritor.writerow(
                [
                    "aleatorio",
                    numero,
                    semente,
                    agente,
                    serializar_posicoes(sujeira),
                    serializar_posicoes(obstaculos),
                    serializar_posicoes([inicio]),
                    resultado["sujeira"],
                    resultado["alcancavel"],
                    resultado["movimentos"],
                    texto_parou(resultado["parou"]),
                    resultado["p1"],
                    resultado["p2"],
                    passos,
                    TAMANHO,
                ]
            )


def _esc(texto):
    return str(texto).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _barras(itens, x, y, largura, altura, titulo):
    """itens: (rotulo, valor, cor, erro). O erro pode ser zero."""
    topo = max((item[1] + item[3]) for item in itens)
    escala = topo * 1.18 if topo else 1
    base = y + 36 + altura
    partes = [
        f'<text x="{x}" y="{y + 18}" font-size="15" font-family="sans-serif" fill="#1d2430">{_esc(titulo)}</text>'
    ]
    for fracao in (0, 0.5, 1):
        yy = base - fracao * altura
        partes.append(
            f'<line x1="{x}" y1="{yy:.1f}" x2="{x + largura}" y2="{yy:.1f}" stroke="#e4e8ee" />'
        )
        partes.append(
            f'<text x="{x - 8}" y="{yy + 4:.1f}" font-size="11" text-anchor="end" '
            f'font-family="sans-serif" fill="#667085">{escala * fracao:.0f}</text>'
        )
    partes.append(
        f'<line x1="{x}" y1="{base}" x2="{x + largura}" y2="{base}" stroke="#98a2b3" />'
    )
    grupo = largura / len(itens)
    largura_barra = min(28, grupo * 0.55)
    for indice, (rotulo, valor, cor, erro) in enumerate(itens):
        centro = x + grupo * indice + grupo / 2
        altura_barra = 0 if escala == 0 else valor / escala * altura
        erro_px = 0 if escala == 0 else erro / escala * altura
        bx = centro - largura_barra / 2
        by = base - altura_barra
        partes.append(
            f'<rect x="{bx:.1f}" y="{by:.1f}" width="{largura_barra:.1f}" '
            f'height="{altura_barra:.1f}" rx="4" fill="{cor}" />'
        )
        if erro:
            baixo = min(base, by + erro_px)
            cima = max(y + 28, by - erro_px)
            partes.append(
                f'<line x1="{centro:.1f}" y1="{cima:.1f}" x2="{centro:.1f}" y2="{baixo:.1f}" '
                f'stroke="#1d2430" stroke-width="1.4" />'
            )
        partes.append(
            f'<text x="{centro:.1f}" y="{by - 8:.1f}" font-size="11" text-anchor="middle" '
            f'font-family="sans-serif" fill="#1d2430">{valor:.0f}</text>'
        )
        partes.append(
            f'<text x="{centro:.1f}" y="{base + 18}" font-size="11" text-anchor="middle" '
            f'font-family="sans-serif" fill="#475467">{_esc(rotulo)}</text>'
        )
    return partes


def salvar_grafico(caminho, fixos, linhas):
    p1 = []
    p2 = []
    for cenario in range(1, len(CENARIOS) + 1):
        simples = next(item for item in fixos if item["cenario"] == cenario and item["agente"] == "Simples")
        memoria = next(item for item in fixos if item["cenario"] == cenario and item["agente"] == "Com memoria")
        p1.append((f"C{cenario} S", simples["p1"], COR_SIMPLES, 0))
        p1.append((f"C{cenario} M", memoria["p1"], COR_MEMORIA, 0))
        p2.append((f"C{cenario} S", simples["p2"], COR_SIMPLES, 0))
        p2.append((f"C{cenario} M", memoria["p2"], COR_MEMORIA, 0))
    resumo = [
        ("S P1", statistics.mean(item["simples_p1"] for item in linhas), COR_SIMPLES,
         dispersao([item["simples_p1"] for item in linhas])),
        ("M P1", statistics.mean(item["memoria_p1"] for item in linhas), COR_MEMORIA,
         dispersao([item["memoria_p1"] for item in linhas])),
        ("S P2", statistics.mean(item["simples_p2"] for item in linhas), COR_SIMPLES,
         dispersao([item["simples_p2"] for item in linhas])),
        ("M P2", statistics.mean(item["memoria_p2"] for item in linhas), COR_MEMORIA,
         dispersao([item["memoria_p2"] for item in linhas])),
    ]
    largura, altura = 980, 760
    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" '
        f'viewBox="0 0 {largura} {altura}">',
        '<rect width="100%" height="100%" fill="#ffffff" />',
        '<text x="48" y="36" font-size="20" font-family="sans-serif" fill="#1d2430">'
        "Pontuacao dos aspiradores</text>",
        f'<text x="48" y="58" font-size="13" font-family="sans-serif" fill="#667085">'
        f"Grade {TAMANHO}x{TAMANHO}. Azul: simples. Verde: com memoria. "
        "Nas medias aleatorias, o traco e o desvio entre cenarios.</text>",
        '<rect x="48" y="78" width="14" height="14" rx="3" fill="#2f6fad" />',
        '<text x="68" y="90" font-size="12" font-family="sans-serif" fill="#1d2430">Simples</text>',
        '<rect x="140" y="78" width="14" height="14" rx="3" fill="#1f8a5b" />',
        '<text x="160" y="90" font-size="12" font-family="sans-serif" fill="#1d2430">Com memoria</text>',
    ]
    partes.extend(_barras(p1, 70, 110, 420, 210, "Cenarios fixos — Pontos 1"))
    partes.extend(_barras(p2, 530, 110, 420, 210, "Cenarios fixos — Pontos 2"))
    partes.extend(
        _barras(
            resumo,
            70,
            430,
            860,
            230,
            f"Media nos {len(linhas)} cenarios aleatorios",
        )
    )
    partes.append("</svg>")
    caminho.write_text("\n".join(partes), encoding="utf-8")


def pacote_animacao(numero, sujeira, obstaculos, inicio, passos):
    simples = simular(ReativoSimples(SEMENTE), sujeira, obstaculos, inicio, passos, registrar=True)
    memoria = simular(ReativoComMemoria(), sujeira, obstaculos, inicio, passos, registrar=True)
    titulo = (
        f"Cenario {numero}: {len(sujeira)} sujos, {len(obstaculos)} obstaculos, inicio {inicio}"
    )
    pacote = {
        "titulo": titulo,
        "tamanho": TAMANHO,
        "obstaculos": [list(posicao) for posicao in sorted(obstaculos)],
        "simples": simples["frames"],
        "memoria": memoria["frames"],
    }
    return pacote, simples, memoria


def salvar_html(caminho, pacotes):
    dados = json.dumps({"cenarios": pacotes}, ensure_ascii=False, separators=(",", ":"))
    dados = dados.replace("<", "\\u003c")
    caminho.write_text(HTML_TEMPLATE.replace("/*__DADOS__*/", dados), encoding="utf-8")


def experimento(passos, n_aleatorios, n_sementes):
    fixos = []
    pacotes = []
    for numero, (sujeira, obstaculos, inicio) in enumerate(CENARIOS, 1):
        pacote, simples, memoria = pacote_animacao(numero, sujeira, obstaculos, inicio, passos)
        pacotes.append(pacote)
        for agente, resultado, semente in (
            ("Simples", simples, SEMENTE),
            ("Com memoria", memoria, ""),
        ):
            fixos.append(
                {
                    "cenario": numero,
                    "agente": agente,
                    "semente": semente,
                    "sujeira_inicial": sujeira,
                    "obstaculos": obstaculos,
                    "inicio": inicio,
                    "passos": passos,
                    **resultado,
                }
            )
    sementes = [SEMENTE + deslocamento for deslocamento in range(n_sementes)]
    linhas, detalhes = avaliar_aleatorios(
        gerar_cenarios(n_aleatorios, SEMENTE), sementes, passos
    )
    imprimir_fixos(fixos)
    imprimir_aleatorios(linhas, sementes)
    csv_caminho = PASTA / "resultados.csv"
    svg_caminho = PASTA / "resultados.svg"
    html_caminho = PASTA / "animacao.html"
    salvar_csv(csv_caminho, fixos, detalhes, passos)
    salvar_grafico(svg_caminho, fixos, linhas)
    salvar_html(html_caminho, pacotes)
    print(f"\nArquivos gerados em {PASTA}:")
    print("  resultados.csv    cada execucao, com o mapa inicial")
    print("  resultados.svg    graficos para a apresentacao")
    print("  animacao.html     passo a passo no navegador")
    print("Animacao no terminal: python3 agentes.py --replay")
    print("Cenario 2, mais devagar: python3 agentes.py --replay --cenario 2 --atraso 0.3")
    return pacotes


def _pintar(texto, cor, colorir):
    if not colorir:
        return texto
    return f"\033[{cor}m{texto}\033[0m"


def _celula_mundo(linha, coluna, frame, obstaculos, colorir):
    posicao = tuple(frame["pos"])
    sujeira = {(l, c) for l, c in frame["sujeira"]}
    agente = (linha, coluna) == posicao
    if (linha, coluna) in obstaculos:
        return _pintar(" # ", "37;100", colorir)
    if agente and (linha, coluna) in sujeira:
        return _pintar(" A ", "30;43", colorir)
    if agente:
        return _pintar(" A ", "97;44", colorir)
    if (linha, coluna) in sujeira:
        return _pintar(" D ", "30;43", colorir)
    return _pintar(" . ", "32", colorir)


def _celula_modelo(linha, coluna, modelo, colorir):
    if not modelo or not modelo.get("pos"):
        return _pintar("   ", "90", colorir)
    posicao = tuple(modelo["pos"])
    estados = {(item["l"], item["c"]): item["estado"] for item in modelo["celulas"]}
    agente = (linha, coluna) == posicao
    estado = estados.get((linha, coluna))
    if estado is None:
        texto, cor = "   ", "90"
    elif estado == "bloqueado":
        texto, cor = " # ", "37;100"
    elif estado == "desconhecido":
        texto, cor = (" A?", "30;43") if agente else (" ? ", "30;43")
    elif estado == "sujo":
        texto, cor = (" A ", "30;43") if agente else (" D ", "30;43")
    else:
        texto, cor = (" A ", "97;44") if agente else (" . ", "32")
    return _pintar(texto, cor, colorir)


def _grade(frame, obstaculos, modelo, colorir):
    mundo = []
    crenca = []
    for linha in range(TAMANHO):
        mundo.append("".join(_celula_mundo(linha, coluna, frame, obstaculos, colorir) for coluna in range(TAMANHO)))
        crenca.append("".join(_celula_modelo(linha, coluna, modelo, colorir) for coluna in range(TAMANHO)))
    return mundo, crenca


def _campo(texto, largura, visiveis):
    return texto + " " * max(0, largura - visiveis)


def reproduzir(pacote, atraso):
    obstaculos = {tuple(posicao) for posicao in pacote["obstaculos"]}
    total = len(pacote["simples"]) - 1
    colorir = sys.stdout.isatty()
    largura = 24
    visiveis_grade = TAMANHO * 3

    def desenhar(indice):
        simples = pacote["simples"][indice]
        memoria = pacote["memoria"][indice]
        grade_s, _ = _grade(simples, obstaculos, None, colorir)
        grade_m, grade_modelo = _grade(memoria, obstaculos, memoria["modelo"], colorir)
        rotulo = "Inicio" if indice == 0 else f"Periodo {indice}/{total}"
        linhas = [
            f"{pacote['titulo']}  |  {rotulo}",
            "A agente   D sujo   . limpo   # obstaculo ou parede   ? passagem ainda nao visitada",
            "",
            _campo("Simples", largura, len("Simples"))
            + _campo("Com memoria", largura, len("Com memoria"))
            + "Modelo interno",
        ]
        for esquerda, centro, direita in zip(grade_s, grade_m, grade_modelo):
            linhas.append(
                _campo(esquerda, largura, visiveis_grade)
                + _campo(centro, largura, visiveis_grade)
                + direita
            )
        linhas.extend(
            [
                "",
                _campo("acao: " + simples["acao"], largura, len("acao: " + simples["acao"]))
                + ("acao: " + memoria["acao"]),
                _campo("Pontos 1: " + str(simples["p1"]), largura, len("Pontos 1: " + str(simples["p1"])))
                + ("Pontos 1: " + str(memoria["p1"])),
                _campo("Pontos 2: " + str(simples["p2"]), largura, len("Pontos 2: " + str(simples["p2"])))
                + ("Pontos 2: " + str(memoria["p2"])),
                _campo("Movimentos: " + str(simples["mov"]), largura, len("Movimentos: " + str(simples["mov"])))
                + ("Movimentos: " + str(memoria["mov"])),
            ]
        )
        if colorir:
            sys.stdout.write("\033[H\033[J")
        print("\n".join(linhas))
        sys.stdout.flush()

    if not colorir:
        desenhar(total)
        print("\nAbra animacao.html no navegador para controlar o passo a passo.")
        return

    try:
        for indice in range(total + 1):
            desenhar(indice)
            if atraso > 0 and indice < total:
                time.sleep(atraso)
    except KeyboardInterrupt:
        print("\nAnimacao interrompida.")


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Aspiradores — passo a passo</title>
<style>
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  body { margin: 0; font-family: "Segoe UI", sans-serif; background: #eef2f6; color: #1d2430; }
  header { padding: 22px 28px 8px; }
  h1 { margin: 0 0 6px; font-size: 26px; }
  p { margin: 0; color: #526070; line-height: 1.4; }
  .controles { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; padding: 14px 28px 0; }
  button, select, input[type="range"] { font: inherit; }
  button, select { background: white; border: 1px solid #cfd6df; border-radius: 8px; padding: 8px 12px; }
  button { cursor: pointer; }
  button.primario { background: #1f8a5b; color: white; border-color: #1f8a5b; }
  label.velocidade { display: flex; align-items: center; gap: 8px; color: #526070; }
  .passo { margin-left: auto; font-weight: 600; }
  .palco { display: flex; flex-wrap: wrap; gap: 18px; padding: 18px 28px 28px; align-items: flex-start; }
  .painel { background: white; border-radius: 16px; padding: 16px 18px 18px; box-shadow: 0 8px 24px rgba(20, 32, 51, 0.06); }
  h2 { margin: 0 0 12px; font-size: 18px; }
  .grade { display: grid; gap: 6px; }
  .cel { width: 58px; height: 58px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 700; }
  .limpo { background: #d7f3e3; color: #0f6b42; }
  .sujo { background: #f6c453; color: #6d5200; }
  .bloqueio { background: #4e5d6c; color: white; }
  .fronteira { background: #fff4dc; color: #8a5a00; border: 2px dashed #e0b15a; }
  .vazio { background: transparent; border: 1px dashed #c5ced8; color: transparent; }
  .agente { box-shadow: inset 0 0 0 4px #1259c3; color: #1259c3; }
  .sujo.agente, .fronteira.agente { color: #1259c3; }
  .numeros { display: grid; grid-template-columns: auto auto; gap: 4px 16px; margin-top: 12px; }
  .numeros span { color: #667085; }
  .numeros strong { font-variant-numeric: tabular-nums; }
  .acao { margin-top: 10px; }
  .legenda { display: flex; flex-wrap: wrap; gap: 12px 18px; list-style: none; padding: 0 28px 28px; margin: 0; }
  .legenda li { display: flex; align-items: center; gap: 8px; }
  .legenda .cel { width: 22px; height: 22px; border-radius: 6px; box-shadow: none; }
  #estado-modelo { margin-top: 12px; color: #365b45; min-height: 1.4em; }
</style>
</head>
<body>
<header>
  <h1>Passo a passo dos aspiradores</h1>
  <p>Os dois agentes recebem o mesmo mapa e agem ao mesmo tempo. O modelo mostra so o que o agente com memoria ja percebeu. Espaco reproduz ou pausa. As setas mudam o periodo.</p>
</header>
<div class="controles">
  <select id="seletor" aria-label="Cenario"></select>
  <button id="play" class="primario">Reproduzir</button>
  <button id="anterior">Anterior</button>
  <button id="proximo">Proximo</button>
  <input id="trilha" type="range" min="0" max="80" value="0" aria-label="Periodo">
  <label class="velocidade">Velocidade <input id="velocidade" type="range" min="40" max="700" value="180"></label>
  <div class="passo" id="rotulo-passo">Inicio</div>
</div>
<div class="palco">
  <section class="painel">
    <h2>Reativo simples</h2>
    <div id="mundo-simples" class="grade"></div>
    <div class="acao">Acao: <strong id="acao-simples">inicio</strong></div>
    <div class="numeros">
      <span>Pontos 1</span><strong id="p1-simples">0</strong>
      <span>Pontos 2</span><strong id="p2-simples">0</strong>
      <span>Movimentos</span><strong id="mov-simples">0</strong>
    </div>
  </section>
  <section class="painel">
    <h2>Reativo com memoria</h2>
    <div id="mundo-memoria" class="grade"></div>
    <div class="acao">Acao: <strong id="acao-memoria">inicio</strong></div>
    <div class="numeros">
      <span>Pontos 1</span><strong id="p1-memoria">0</strong>
      <span>Pontos 2</span><strong id="p2-memoria">0</strong>
      <span>Movimentos</span><strong id="mov-memoria">0</strong>
    </div>
  </section>
  <section class="painel">
    <h2>Modelo interno</h2>
    <div id="grade-modelo" class="grade"></div>
    <p id="estado-modelo"></p>
  </section>
</div>
<ul class="legenda">
  <li><span class="cel limpo"></span> limpo</li>
  <li><span class="cel sujo"></span> sujo</li>
  <li><span class="cel bloqueio"></span> obstaculo ou parede</li>
  <li><span class="cel fronteira"></span> passagem ainda nao visitada</li>
  <li><span class="cel vazio"></span> ainda fora do modelo</li>
  <li><span class="cel limpo agente">A</span> agente</li>
</ul>
<script>
const DADOS = /*__DADOS__*/;
let indice = Math.min(1, DADOS.cenarios.length - 1);
let quadro = 0;
let reproduzindo = false;
let timer = null;

function chave(l, c) { return l + "," + c; }
function atraso() { return Number(document.getElementById("velocidade").value); }
function atual() { return DADOS.cenarios[indice]; }
function ultimo() { return atual().simples.length - 1; }

function preparar(cenario) {
  if (!cenario.bloqueios) {
    cenario.bloqueios = new Set(cenario.obstaculos.map(([l, c]) => chave(l, c)));
  }
}

function celula(classe, texto, titulo) {
  const elemento = document.createElement("div");
  elemento.className = "cel " + classe;
  elemento.textContent = texto || "";
  if (titulo) elemento.title = titulo;
  return elemento;
}

function desenharMundo(id, cenario, frame) {
  const grade = document.getElementById(id);
  grade.innerHTML = "";
  grade.style.gridTemplateColumns = "repeat(" + cenario.tamanho + ", 58px)";
  const sujos = new Set(frame.sujeira.map(([l, c]) => chave(l, c)));
  const al = frame.pos[0];
  const ac = frame.pos[1];
  for (let l = 0; l < cenario.tamanho; l++) {
    for (let c = 0; c < cenario.tamanho; c++) {
      const idc = chave(l, c);
      let classe = "limpo";
      if (cenario.bloqueios.has(idc)) classe = "bloqueio";
      else if (sujos.has(idc)) classe = "sujo";
      if (l === al && c === ac) classe += " agente";
      grade.appendChild(celula(classe, l === al && c === ac ? "A" : ""));
    }
  }
}

function desenharModelo(cenario, frame) {
  const grade = document.getElementById("grade-modelo");
  grade.innerHTML = "";
  grade.style.gridTemplateColumns = "repeat(" + cenario.tamanho + ", 58px)";
  const info = new Map();
  const modelo = frame.modelo || {pos: null, celulas: []};
  modelo.celulas.forEach((cel) => info.set(chave(cel.l, cel.c), cel));
  const pos = modelo.pos;
  for (let l = 0; l < cenario.tamanho; l++) {
    for (let c = 0; c < cenario.tamanho; c++) {
      const item = info.get(chave(l, c));
      let classe = "vazio";
      let titulo = "";
      if (item) {
        classe = {limpo: "limpo", sujo: "sujo", bloqueado: "bloqueio", desconhecido: "fronteira"}[item.estado] || "vazio";
        titulo = "Visitas: " + item.visitas;
      }
      const agente = pos && pos[0] === l && pos[1] === c;
      if (agente) classe += " agente";
      grade.appendChild(celula(classe, agente ? "A" : (item && item.estado === "desconhecido" ? "?" : ""), titulo));
    }
  }
  const porVisitar = modelo.celulas.filter((cel) => cel.estado === "desconhecido").length;
  const sujas = modelo.celulas.filter((cel) => cel.estado === "sujo").length;
  let texto = "Por visitar: " + porVisitar + " · Sujeira conhecida: " + sujas;
  if (frame.acao === "parar") texto += " · Decidiu parar.";
  document.getElementById("estado-modelo").textContent = texto;
}

function preencher(prefixo, frame) {
  document.getElementById("acao-" + prefixo).textContent = frame.acao;
  document.getElementById("p1-" + prefixo).textContent = frame.p1;
  document.getElementById("p2-" + prefixo).textContent = frame.p2;
  document.getElementById("mov-" + prefixo).textContent = frame.mov;
}

function render() {
  const cenario = atual();
  preparar(cenario);
  const simples = cenario.simples[quadro];
  const memoria = cenario.memoria[quadro];
  desenharMundo("mundo-simples", cenario, simples);
  desenharMundo("mundo-memoria", cenario, memoria);
  desenharModelo(cenario, memoria);
  preencher("simples", simples);
  preencher("memoria", memoria);
  document.getElementById("rotulo-passo").textContent = quadro === 0 ? "Inicio" : "Periodo " + quadro + " de " + ultimo();
  const trilha = document.getElementById("trilha");
  trilha.max = ultimo();
  trilha.value = quadro;
}

function parar() {
  reproduzindo = false;
  if (timer) clearTimeout(timer);
  timer = null;
  document.getElementById("play").textContent = "Reproduzir";
}

function tick() {
  if (!reproduzindo) return;
  if (quadro >= ultimo()) { parar(); return; }
  quadro += 1;
  render();
  timer = setTimeout(tick, atraso());
}

function reproduzir() {
  if (reproduzindo) { parar(); return; }
  if (quadro >= ultimo()) quadro = 0;
  reproduzindo = true;
  document.getElementById("play").textContent = "Pausar";
  render();
  timer = setTimeout(tick, atraso());
}

function iniciar() {
  const seletor = document.getElementById("seletor");
  DADOS.cenarios.forEach((cenario, i) => {
    const opcao = document.createElement("option");
    opcao.value = String(i);
    opcao.textContent = cenario.titulo;
    seletor.appendChild(opcao);
  });
  seletor.value = String(indice);
  seletor.addEventListener("change", () => {
    parar();
    indice = Number(seletor.value);
    quadro = 0;
    render();
  });
  document.getElementById("play").addEventListener("click", reproduzir);
  document.getElementById("anterior").addEventListener("click", () => {
    parar();
    quadro = Math.max(0, quadro - 1);
    render();
  });
  document.getElementById("proximo").addEventListener("click", () => {
    parar();
    quadro = Math.min(ultimo(), quadro + 1);
    render();
  });
  document.getElementById("trilha").addEventListener("input", (evento) => {
    parar();
    quadro = Number(evento.target.value);
    render();
  });
  document.addEventListener("keydown", (evento) => {
    const tag = evento.target.tagName;
    if (tag === "SELECT" || tag === "INPUT") return;
    if (evento.key === "ArrowRight") {
      parar();
      quadro = Math.min(ultimo(), quadro + 1);
      render();
    } else if (evento.key === "ArrowLeft") {
      parar();
      quadro = Math.max(0, quadro - 1);
      render();
    } else if (evento.key === " ") {
      evento.preventDefault();
      reproduzir();
    }
  });
  render();
}
iniciar();
</script>
</body>
</html>
"""


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Avalia um aspirador reativo simples e outro baseado em modelo."
    )
    if not CENARIOS:
        parser.error("Adicione pelo menos um cenario em CENARIOS.")
    parser.add_argument("--replay", action="store_true", help="Anima um cenario fixo no terminal")
    parser.add_argument("--cenario", type=int, default=min(2, len(CENARIOS)), choices=range(1, len(CENARIOS) + 1))
    parser.add_argument("--atraso", type=float, default=0.2, help="Segundos entre passos da animacao")
    parser.add_argument("--aleatorios", type=int, default=CENARIOS_ALEATORIOS)
    parser.add_argument("--sementes", type=int, default=SEMENTES_SIMPLES)
    parser.add_argument("--passos", type=int, default=PASSOS)
    args = parser.parse_args(argv)
    if args.passos < 1 or args.aleatorios < 1 or args.sementes < 1:
        parser.error("passos, aleatorios e sementes precisam ser maiores que zero.")
    if args.atraso < 0:
        parser.error("atraso nao pode ser negativo.")

    if args.replay:
        sujeira, obstaculos, inicio = CENARIOS[args.cenario - 1]
        pacote, _, _ = pacote_animacao(args.cenario, sujeira, obstaculos, inicio, args.passos)
        reproduzir(pacote, args.atraso)
        return

    experimento(args.passos, args.aleatorios, args.sementes)


if __name__ == "__main__":
    main()
