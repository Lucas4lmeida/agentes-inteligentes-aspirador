# Agentes inteligentes: aspirador de pó

Comparação entre um agente reativo simples e um agente reativo baseado em modelo, em uma grade determinística e parcialmente observável.

## Executar

Requer Python 3. Não usa bibliotecas externas.

```bash
python3 agentes.py
```

Isso imprime os três cenários fixos, trinta configurações aleatórias e grava:

- `resultados.csv` — cada execução, com o mapa inicial
- `resultados.svg` — gráficos das duas pontuações
- `animacao.html` — passo a passo no navegador

Para ver o mesmo passo a passo no terminal, no cenário em que o agente simples deixa sujeira:

```bash
python3 agentes.py --replay
python3 agentes.py --replay --cenario 2 --atraso 0.3
```

No navegador, abra `animacao.html`. Espaço reproduz ou pausa. As setas mudam o período.

## Alterar os testes

As configurações ficam no início de `agentes.py`:

```python
SEMENTE = 42
PASSOS = 80
TAMANHO = 4
CENARIOS_ALEATORIOS = 30
SEMENTES_SIMPLES = 5
```

`CENARIOS` guarda os três mapas fixos: sujeira, obstáculos e posição inicial. As coordenadas começam em zero. Execute de novo depois de alterar o arquivo. O programa regrava a tabela, o gráfico e a animação.

## Agentes

Os sensores informam apenas a sujeira no quadrado atual e as passagens vizinhas livres. Os agentes não recebem o mapa nem as dimensões. O ambiente é determinístico. O sorteio do agente simples escolhe a ação; a mesma ação no mesmo estado tem sempre o mesmo efeito.

- **Reativo simples:** se está sujo, aspira. Senão, sorteia uma passagem livre. Não guarda os lugares visitados. A semente 42 repete o sorteio.
- **Reativo com memória:** mantém a posição relativa ao início, as células conhecidas (limpa, bloqueada ou ainda não visitada) e a quantidade de visitas. A cada período: atualiza esse estado com o percepto; se está sujo, aspira; senão dá um passo em direção à sujeira conhecida ou à célula não visitada mais próxima; se não há trabalho no mapa, para. Entre passos equivalentes, prefere o menos visitado e, no empate, a ordem direita, baixo, esquerda e cima.

## Experimento

- Grade fixa de 4 por 4.
- Três cenários fixos, com quatro quadrados sujos.
- Trinta cenários aleatórios, com sujeira, obstáculos e posição inicial variando. A semente 42 gera esses mapas.
- O agente simples repete cada cenário aleatório com as sementes 42 a 46.
- 80 períodos, uma ação por período.
- Não aparece sujeira nova.

**Pontos 1:** soma dos quadrados limpos ao fim de cada período. Obstáculos não pontuam.

**Pontos 2:** Pontos 1 menos a quantidade de movimentos.

## Resultados dos cenários fixos

```text
Cenario Agente         Sujeira  Alc.  Mov.  Parou  Pontos 1  Pontos 2
1       Simples              0     0    76      -      1174      1098
1       Com memoria          0     0    15     20      1256      1241
2       Simples              1     1    77      -      1009       932
2       Com memoria          0     0    13     18      1083      1070
3       Simples              0     0    76      -      1009       933
3       Com memoria          0     0    19     24      1071      1052

Medias:
Simples:     Pontos 1 = 1064.00 | Pontos 2 = 987.67
Com memoria: Pontos 1 = 1136.67 | Pontos 2 = 1121.00
```

Alc. é a sujeira restante que ainda dava para alcançar. Parou é o período em que a parada começou.

Nos trinta cenários aleatórios, a média de Pontos 2 foi 1031,60 para o agente simples e 1146,80 para o agente com memória. O agente com memória teve Pontos 2 maior nos 30 casos e removeu a sujeira alcançável em todos. O agente simples fez isso em 127 de 150 execuções.

O agente com memória limpa a região conhecida e para. O agente simples continua andando até o período 80. Isso aumenta a diferença na segunda pontuação, porque cada movimento extra desconta um ponto.

## Apresentação

- [Gráfico](resultados.svg)
- [Passo a passo](animacao.html)
- [Roteiro de fala](roteiro_apresentacao.md)
