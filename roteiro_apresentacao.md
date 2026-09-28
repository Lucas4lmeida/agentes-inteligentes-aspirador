# Roteiro de apresentação

Tempo sugerido: aproximadamente 7 minutos e 30 segundos. As mesmas falas estão nas notas dos slides.

## Slide 1: Avaliação experimental de agentes inteligentes

Tempo sugerido: 1 minuto

O objetivo foi comparar dois aspiradores: um reativo simples e outro reativo baseado em modelos, que chamamos de agente com memória. Criamos um ambiente 4 por 4, com quatro quadrados inicialmente sujos em cada cenário. O primeiro cenário não tem obstáculos, e os outros dois têm dois obstáculos cada. Também mudamos a posição inicial e a distribuição da sujeira. Cada agente roda separadamente por 80 períodos, nas mesmas condições iniciais. O mundo é determinístico: uma ação nas mesmas condições tem sempre o mesmo efeito. A escolha aleatória do agente simples não altera essa propriedade. A observação é parcial: os agentes detectam apenas a sujeira onde estão e as passagens vizinhas. Eles não recebem o mapa nem suas dimensões. Não surge sujeira nova.

## Slide 2: Como os agentes escolhem suas ações

Tempo sugerido: 1 minuto e 30 segundos

Os dois agentes usam regras condição-ação. A primeira regra é igual: se o quadrado atual está sujo, aspirar. Se estiver limpo, o agente simples sorteia uma passagem livre. Ele não registra os lugares que visitou. A semente 42 permite repetir as escolhas e os resultados. O outro agente mantém uma posição relativa ao ponto de partida e um dicionário com o número de visitas a cada posição. O início recebe uma visita e posições desconhecidas valem zero. Quando se move, ele atualiza sua posição e aumenta a contagem do destino. Entre as passagens livres, escolhe o destino menos visitado. Em empate, segue a ordem direita, baixo, esquerda e cima. Como o sensor informa passagem livre e o ambiente é determinístico, essa atualização corresponde ao movimento real. Sem passagem livre, os agentes ficam parados naquele período.

## Slide 3: Regras de avaliação

Tempo sugerido: 1 minuto

Cada ação ocupa um período, incluindo aspirar. Calculamos a primeira medida somando o número de quadrados limpos ao fim de cada um dos 80 períodos. Os quadrados que já estavam limpos também contam, e os obstáculos ficam fora da conta. Se houver seis quadrados limpos em um período, ganhamos seis pontos naquele período. Se continuarem limpos no próximo, ganhamos mais seis. Por isso, limpar cedo é vantajoso. Para a segunda medida, adotamos a primeira pontuação menos o número de movimentos realizados. O enunciado não repete a expressão em cada período ao descrever a segunda medida, então essa é uma interpretação explicitamente assumida. Aspirar ocupa tempo, mas não sofre o desconto de movimento. O simulador conhece todo o ambiente para pontuar, mas os agentes só recebem informações locais.

## Slide 4: Resultados dos três cenários

Tempo sugerido: 1 minuto e 30 segundos

Esta tabela mostra as seis execuções, com um teste por agente em cada cenário. O agente com memória terminou sem sujeira em todos os casos. O simples deixou um quadrado sujo no cenário dois. Quando um agente limpa os quatro quadrados, gasta quatro ações aspirando e 76 se movendo. No cenário dois, o simples aspira três vezes e se move 77 vezes. As pontuações mostram também quando ele limpou: nos cenários um e três, ambos terminaram sem sujeira e fizeram o mesmo número de movimentos, mas o agente com memória obteve mais pontos por limpar mais cedo no conjunto da execução. As médias abaixo usam os três cenários com o mesmo peso. Comparamos os agentes dentro de cada cenário, pois a presença de obstáculos altera a quantidade de quadrados que podem pontuar.

## Slide 5: Comparação das pontuações

Tempo sugerido: 1 minuto

Os gráficos mostram as mesmas pontuações da tabela. Azul representa o agente simples e verde representa o agente com memória. Cada grupo reúne os dois agentes no mesmo cenário. O gráfico da esquerda mostra a limpeza acumulada e o da direita desconta os movimentos. Ambos começam em zero e usam a mesma escala. O agente com memória ficou à frente nos três cenários, nas duas medidas. A diferença média foi de aproximadamente 70,67 pontos na primeira medida e 71 pontos na segunda. A penalização quase não altera a comparação, porque o número de movimentos é praticamente igual. Estes resultados se referem a três configurações fixas e a uma única semente do agente simples, sem estimar a variabilidade de outras escolhas aleatórias.

## Slide 6: Racionalidade e limites do experimento

Tempo sugerido: 1 minuto e 30 segundos

Racionalidade significa escolher ações adequadas à medida de desempenho, considerando a informação disponível. A memória permitiu usar o histórico para orientar a exploração e favoreceu a limpeza mais cedo nestes testes. Isso explica as maiores pontuações. Entretanto, o agente não é necessariamente ótimo. Os dois continuam andando até completar 80 períodos e não reconhecem que toda a região acessível está limpa. Depois da limpeza completa, esses movimentos deixam de ajudar e reduzem a segunda pontuação. O simulador sabe que acabou a sujeira, mas essa informação global não é entregue aos agentes. A conclusão é que o agente com memória teve melhor desempenho nos testes realizados, e não que sempre será melhor. Para ampliar a evidência, podemos repetir com outras sementes e configurações. Uma melhoria futura seria construir um mapa dos locais descobertos e reconhecer o término da exploração antes de decidir parar.

## Respostas rápidas

- Por que os resultados se repetem? Os cenários são fixos e o agente simples usa a semente 42.
- Por que 76 movimentos? Foram 80 ações, sendo quatro aspirações e 76 movimentos.
- Como pode ser determinístico se há sorteio? O sorteio escolhe a ação. A mesma ação no mesmo estado tem sempre o mesmo efeito.
- O agente com memória conhece o mapa? Não. Ele registra posições relativas e visitas conforme se movimenta.
- Por que o agente não para quando termina? Esta versão não tem um mecanismo para reconhecer a limpeza completa.
- A segunda medida é exatamente a do professor? Adotamos limpeza acumulada menos movimentos. É preciso confirmar a interpretação, pois o texto não repete “em cada período” na segunda medida.

Fontes: enunciado do Projeto 1, páginas 1 e 2, e execução de agentes.py.
