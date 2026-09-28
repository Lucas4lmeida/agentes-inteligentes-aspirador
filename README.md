# Agentes inteligentes: aspirador de pó

Comparação simples entre um agente reativo simples e um agente reativo baseado em modelos, usando Python no terminal.

## Executar

Requer Python 3. Nao usa bibliotecas externas.

```bash
python agentes.py
```

## Agentes

- **Reativo simples:** aspira quando encontra sujeira. Caso contrario, sorteia um caminho livre, sem guardar os locais visitados.
- **Reativo com memória:** aspira quando encontra sujeira. Caso contrario, escolhe o vizinho menos visitado. Guarda a posição relativa ao inicio e a quantidade de visitas.

Os sensores informam apenas a sujeira no quadrado atual e as passagens vizinhas livres. Os agentes nao recebem o mapa nem suas dimensoes. O ambiente e deterministico, mesmo que o agente simples use sorteio para escolher suas acoes.

## Experimento

- Grade fixa de 4 por 4 quadrados.
- Tres cenarios com diferentes sujeiras, obstaculos e posicoes iniciais.
- Quatro quadrados inicialmente sujos por cenario.
- 80 periodos por execucao, com uma acao por periodo.
- Mesmas configuracoes iniciais para os dois agentes.
- Semente 42 no sorteio, para reproduzir os resultados.
- Não aparece sujeira nova.

**Pontos 1:** soma dos quadrados limpos ao fim de cada periodo, incluindo os que ja estavam limpos. Obstaculos nao pontuam.

**Pontos 2:** Pontos 1 menos a quantidade de movimentos realizados. Esta e a interpretacao adotada para a segunda medida do enunciado.

## Resultados

```text
Cenario  Agente          Sujeira final   Movimentos   Pontos 1   Pontos 2
1        Simples                     0           76       1174       1098
1        Com memoria                 0           76       1256       1180
2        Simples                     1           77       1009        932
2        Com memoria                 0           76       1083       1007
3        Simples                     0           76       1009        933
3        Com memoria                 0           76       1065        989

Medias:
Simples:     Pontos 1 = 1064.00 | Pontos 2 = 987.67
Com memoria: Pontos 1 = 1134.67 | Pontos 2 = 1058.67
```

O agente com memoria pontuou mais nesses tres cenarios. Limpar cedo aumenta a recompensa acumulada. Os dois continuam andando ate completar 80 periodos, inclusive depois de limpar tudo. A versao atual nao reconhece o termino da limpeza.

Os resultados usam uma unica semente e nao demonstram superioridade em qualquer ambiente. Outras sementes e configuracoes podem ampliar a avaliacao.

## Apresentacao

- [Slides com tabela e graficos](apresentacao_agentes.pptx)
- [Roteiro de fala e perguntas frequentes](roteiro_apresentacao.md)

A apresentacao tem seis slides, com tempo sugerido de aproximadamente 7 a 8 minutos. As falas tambem estao nas notas dos slides.
