"""Dois aspiradores simples. Execute com: python agentes.py

Sensores: sujeira no quadrado atual e direcoes vizinhas livres.
Os agentes nao recebem o mapa, seu tamanho ou a sujeira dos vizinhos.
Cada acao ocupa um periodo. Nao aparece sujeira nova.
Pontuacao 1: soma dos quadrados limpos ao fim de cada periodo.
Pontuacao 2: pontuacao 1 menos movimentos realizados (interpretacao adotada).
Obstaculos nao contam como quadrados limpos.
"""

import random


DIRECOES = ((0, 1), (1, 0), (0, -1), (-1, 0))
ASPIRAR = "aspirar"
PARAR = "parar"
TAMANHO = 4
PERIODOS = 80


class ReativoSimples:
    def __init__(self, semente=42):
        self.sorteio = random.Random(semente)

    def agir(self, sujo, caminhos):
        if sujo:
            return ASPIRAR
        if caminhos:
            return self.sorteio.choice(caminhos)
        return PARAR


class ReativoComMemoria:
    def __init__(self):
        # Coordenadas relativas ao inicio, sem conhecer o mapa real.
        self.posicao = (0, 0)
        self.visitas = {(0, 0): 1}

    def agir(self, sujo, caminhos):
        if sujo:
            return ASPIRAR
        if not caminhos:
            return PARAR

        linha, coluna = self.posicao
        direcao = min(
            caminhos,
            key=lambda d: self.visitas.get((linha + d[0], coluna + d[1]), 0),
        )
        # O sensor garante passagem livre; o movimento nao falha neste mundo.
        self.posicao = (linha + direcao[0], coluna + direcao[1])
        self.visitas[self.posicao] = self.visitas.get(self.posicao, 0) + 1
        return direcao


def simular(agente, sujeira_inicial, obstaculos, inicio, periodos=PERIODOS):
    sujeira = set(sujeira_inicial)
    posicao = inicio
    movimentos = 0
    pontos = 0
    quadrados_livres = TAMANHO * TAMANHO - len(obstaculos)

    for _ in range(periodos):
        linha, coluna = posicao
        caminhos = []
        for dl, dc in DIRECOES:
            vizinho = (linha + dl, coluna + dc)
            if (
                0 <= vizinho[0] < TAMANHO
                and 0 <= vizinho[1] < TAMANHO
                and vizinho not in obstaculos
            ):
                caminhos.append((dl, dc))

        acao = agente.agir(posicao in sujeira, caminhos)
        if acao == ASPIRAR:
            sujeira.discard(posicao)
        elif acao != PARAR:
            dl, dc = acao
            posicao = (linha + dl, coluna + dc)
            movimentos += 1

        pontos += quadrados_livres - len(sujeira)

    return len(sujeira), movimentos, pontos, pontos - movimentos


def main():
    # Cada cenario: sujeira inicial, obstaculos, posicao inicial.
    cenarios = [
        ({(0, 0), (0, 3), (3, 0), (3, 3)}, set(), (0, 0)),
        ({(0, 2), (1, 3), (2, 0), (3, 2)}, {(1, 1), (2, 1)}, (3, 0)),
        ({(0, 0), (1, 0), (2, 2), (3, 3)}, {(1, 2), (2, 1)}, (0, 3)),
    ]
    tipos = [("Simples", ReativoSimples), ("Com memoria", ReativoComMemoria)]
    totais = {nome: [0, 0] for nome, _ in tipos}

    print(f"Ambiente: {TAMANHO}x{TAMANHO} | Periodos por execucao: {PERIODOS}")
    print("Pontos 1: limpeza acumulada | Pontos 2: Pontos 1 - movimentos")
    print("O agente simples usa sorteio com semente 42 para repetir o teste.\n")
    print(f"{'Cenario':<9}{'Agente':<15}{'Sujeira final':>14}{'Movimentos':>13}"
          f"{'Pontos 1':>11}{'Pontos 2':>11}")

    for numero, (sujeira, obstaculos, inicio) in enumerate(cenarios, 1):
        for nome, classe in tipos:
            restante, movimentos, p1, p2 = simular(classe(), sujeira, obstaculos, inicio)
            totais[nome][0] += p1
            totais[nome][1] += p2
            print(f"{numero:<9}{nome:<15}{restante:>14}{movimentos:>13}"
                  f"{p1:>11}{p2:>11}")

    print("\nMedia das pontuacoes nos tres cenarios:")
    for nome, (p1, p2) in totais.items():
        print(f"{nome}: Pontos 1 = {p1 / len(cenarios):.2f} | "
              f"Pontos 2 = {p2 / len(cenarios):.2f}")


if __name__ == "__main__":
    main()
