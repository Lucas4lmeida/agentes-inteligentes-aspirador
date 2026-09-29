# Roteiro de apresentação

Tempo sugerido: cerca de 8 minutos. Se for projetar a animação, use só o cenário 2 e avance até o período 18, quando o agente com memória para.

## Slide 1: Avaliação experimental de agentes inteligentes

Tempo sugerido: 1 minuto

O objetivo foi comparar dois aspiradores: um reativo simples e outro reativo baseado em modelo. O ambiente é uma grade 4 por 4, determinística e parcialmente observável. Os agentes percebem a sujeira da célula atual e as passagens vizinhas. Não recebem o mapa, o tamanho, os obstáculos nem a sujeira distante. Não surge sujeira nova. Há três mapas fixos e trinta mapas aleatórios, com a mesma condição inicial para os dois programas.

## Slide 2: Como os agentes escolhem suas ações

Tempo sugerido: 1 minuto e 40 segundos

Os dois usam regras condição-ação. A primeira é igual: se o quadrado atual está sujo, aspirar.

O agente simples, se está limpo, sorteia uma passagem livre. Não registra o que já viu. A semente 42 repete as escolhas.

O agente com memória guarda um estado interno em coordenadas relativas ao ponto de partida: células limpas, bloqueadas ou ainda não visitadas, e o número de visitas. A cada período ele faz três coisas. Primeiro, atualiza o estado com o percepto local. Depois, aplica a regra: se há sujeira conhecida ou célula não visitada, dá um passo em direção à mais próxima; se não há, para. No empate, prefere o vizinho menos visitado e, depois, a ordem direita, baixo, esquerda e cima. Por último, aplica a ação no próprio modelo, porque o sensor já informou que a passagem está livre e o efeito no mundo é determinístico.

A sujeira distante não entra no mapa. O sensor só acusa sujeira debaixo do agente, e a regra aspira nessa mesma hora.

## Slide 3: Regras de avaliação

Tempo sugerido: 1 minuto

Cada ação ocupa um período, inclusive aspirar. A primeira medida soma os quadrados limpos ao fim de cada um dos 80 períodos. Quadrados que já estavam limpos também contam. Obstáculos ficam de fora. Limpar cedo aumenta essa soma. A segunda medida é a primeira menos o número de movimentos. Aspirar gasta tempo, mas não entra nesse desconto. O simulador conhece o ambiente inteiro para pontuar. Os agentes recebem só a informação local.

## Slide 4: Resultados dos três cenários

Tempo sugerido: 1 minuto e 30 segundos

| Cenário | Agente | Sujeira | Alc. | Mov. | Parou | Pontos 1 | Pontos 2 |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | Simples | 0 | 0 | 76 | — | 1174 | 1098 |
| 1 | Com memória | 0 | 0 | 15 | 20 | 1256 | 1241 |
| 2 | Simples | 1 | 1 | 77 | — | 1009 | 932 |
| 2 | Com memória | 0 | 0 | 13 | 18 | 1083 | 1070 |
| 3 | Simples | 0 | 0 | 76 | — | 1009 | 933 |
| 3 | Com memória | 0 | 0 | 19 | 24 | 1071 | 1052 |

Médias: simples, 1064,00 e 987,67; com memória, 1136,67 e 1121,00.

Alc. é a sujeira que ainda dava para alcançar. No cenário 2 o agente simples termina com um quadrado sujo alcançável. O agente com memória limpa os quatro nos três mapas e para entre os períodos 18 e 24. A primeira pontuação sobe porque a limpeza acontece mais cedo. A segunda sobe também porque, depois disso, ele não continua se movendo.

## Slide 5: Comparação das pontuações

Tempo sugerido: 1 minuto e 20 segundos

O gráfico em `resultados.svg` repete os três cenários e mostra a média dos trinta mapas aleatórios, com o desvio entre configurações. Azul é o agente simples e verde é o agente com memória.

Nesses trinta mapas, a média de Pontos 1 foi 1108,29 para o simples e 1162,20 para o com memória. A média de Pontos 2 foi 1031,60 e 1146,80. O desvio entre cenários ficou em torno de 77 pontos para o simples e 64 para o com memória. O agente com memória teve Pontos 2 maior nos 30 casos. Ele removeu a sujeira alcançável em todos. O simples fez isso em 127 das 150 execuções, contando cinco sementes por mapa.

A animação do cenário 2 mostra o comportamento por trás da tabela: o simples volta a células já limpas e deixa uma suja; o com memória cobre a fronteira do mapa e, no período 18, a ação passa a ser parar. O contador de movimentos dele trava em 13. O do simples segue até 77.

## Slide 6: Racionalidade e limites do experimento

Tempo sugerido: 1 minuto e 30 segundos

Racionalidade é escolher a ação adequada à medida de desempenho, com a informação disponível. O mapa interno permite explorar sem repetir à toa e reconhecer quando a região conhecida está limpa. Parar nesse momento é adequado à segunda medida: cada movimento depois da limpeza desconta um ponto e não aumenta a limpeza. O agente simples não tem como saber disso, porque esquece o que já percebeu.

Isso não torna o programa ótimo em qualquer mundo. A grade tem tamanho fixo, os trinta mapas usam até dois obstáculos e o sorteio do agente simples está limitado a cinco sementes. A conclusão é que, nestes testes, o agente com memória foi mais adequado às duas medidas, em especial à que penaliza movimento.

## Respostas rápidas

- Como alterar os testes? No início de `agentes.py`, mude `SEMENTE`, `PASSOS`, `TAMANHO`, `CENARIOS` ou a quantidade de cenários aleatórios e execute de novo.
- Como ver o passo a passo? `python3 agentes.py --replay` ou abra `animacao.html`.
- Por que os resultados se repetem? Os mapas e as sementes estão fixos.
- Por que o agente com memória faz tão poucos movimentos? Ele aspira, percorre a área alcançável e para. No cenário 1 são 15 movimentos e 4 aspirações; a parada começa no período 20.
- Como pode ser determinístico se há sorteio? O sorteio escolhe a ação. A mesma ação no mesmo estado tem sempre o mesmo efeito.
- O agente com memória conhece o mapa desde o início? Não. Ele registra células relativas e visitas conforme percebe o ambiente.
- A segunda medida é exatamente a do enunciado? Usamos a limpeza acumulada menos o total de movimentos. O texto não repete “em cada período” na segunda medida; esta leitura fica explícita.

Fontes: enunciado do Projeto 1 e execução de `agentes.py`.
