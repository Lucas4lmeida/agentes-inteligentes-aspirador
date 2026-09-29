"""Dois aspiradores simples. Execute com: python agentes.py

Sensores: sujeira no quadrado atual e direcoes vizinhas livres.
Os agentes nao recebem o mapa, seu tamanho ou a sujeira dos vizinhos.
Cada acao ocupa um periodo. Nao aparece sujeira nova.
Pontuacao 1: soma dos quadrados limpos ao fim de cada periodo.
Pontuacao 2: pontuacao 1 menos movimentos realizados (interpretacao adotada).
Obstaculos nao contam como quadrados limpos.
"""

import random


# CONFIGURACOES: altere estes valores para fazer outros testes.
SEMENTE = 42  # Mesma semente repete as escolhas do agente simples.
PASSOS = 80  # Total de acoes por execucao, incluindo aspirar.
TAMANHO = 4  # Quantidade de linhas e colunas da grade.

# Cada cenario: sujeira inicial, obstaculos, posicao inicial.
# Posicoes usam (linha, coluna), de 0 ate TAMANHO - 1.
CENARIOS = [
    ({(0, 0), (0, 3), (3, 0), (3, 3)}, set(), (0, 0)),
    ({(0, 2), (1, 3), (2, 0), (3, 2)}, {(1, 1), (2, 1)}, (3, 0)),
    ({(0, 0), (1, 0), (2, 2), (3, 3)}, {(1, 2), (2, 1)}, (0, 3)),
]

# Regras fixas: direita, baixo, esquerda e cima.
DIRECOES = ((0, 1), (1, 0), (0, -1), (-1, 0))
ASPIRAR = "aspirar"
PARAR = "parar"


class ReativoSimples:
    def __init__(self, semente=SEMENTE):
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


def simular(agente, sujeira_inicial, obstaculos, inicio, periodos=PASSOS):
    if TAMANHO < 1 or periodos < 1:
        raise ValueError("TAMANHO e PASSOS devem ser maiores que zero.")
    posicoes = set(sujeira_inicial) | set(obstaculos) | {inicio}
    if any(not (0 <= l < TAMANHO and 0 <= c < TAMANHO) for l, c in posicoes):
        raise ValueError("Ajuste CENARIOS: ha posicoes fora do TAMANHO da grade.")
    if inicio in obstaculos or set(sujeira_inicial) & set(obstaculos):
        raise ValueError("O inicio e a sujeira nao podem ficar em obstaculos.")

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
    if not CENARIOS:
        raise ValueError("Adicione pelo menos um cenario em CENARIOS.")
    tipos = [("Simples", ReativoSimples), ("Com memoria", ReativoComMemoria)]
    totais = {nome: [0, 0] for nome, _ in tipos}

    print(f"Ambiente: {TAMANHO}x{TAMANHO} | Passos por execucao: {PASSOS}")
    print("Pontos 1: limpeza acumulada | Pontos 2: Pontos 1 - movimentos")
    print(f"O agente simples usa sorteio com semente {SEMENTE} para repetir o teste.\n")
    print(f"{'Cenario':<9}{'Agente':<15}{'Sujeira final':>14}{'Movimentos':>13}"
          f"{'Pontos 1':>11}{'Pontos 2':>11}")

    for numero, (sujeira, obstaculos, inicio) in enumerate(CENARIOS, 1):
        for nome, classe in tipos:
            restante, movimentos, p1, p2 = simular(classe(), sujeira, obstaculos, inicio)
            totais[nome][0] += p1
            totais[nome][1] += p2
            print(f"{numero:<9}{nome:<15}{restante:>14}{movimentos:>13}"
                  f"{p1:>11}{p2:>11}")

    print(f"\nMedia das pontuacoes nos {len(CENARIOS)} cenarios:")
    for nome, (p1, p2) in totais.items():
        print(f"{nome}: Pontos 1 = {p1 / len(CENARIOS):.2f} | "
              f"Pontos 2 = {p2 / len(CENARIOS):.2f}")


if __name__ == "__main__":
    main()
