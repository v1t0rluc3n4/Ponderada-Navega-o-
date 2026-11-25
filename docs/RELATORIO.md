# Desafio de navegação autônoma

## 1. Objetivo e modelagem

Resolver duas tarefas: encontrar uma rota ótima usando o mapa completo e construir,
durante a navegação, um mapa suficiente para reproduzir essa rota sem consultar o
mapa global. Cada célula livre é um vértice. Duas células livres compartilham uma
aresta se forem vizinhas horizontal ou verticalmente. Cada movimento custa 1.
As oito posições dos sensores podem ser observadas, mas apenas quatro direções
são usadas para deslocamento. Coordenadas são pares (linha, coluna), base zero.

Símbolos: `b` parede, `f` livre, `r` robô, `t` alvo. Células ainda desconhecidas
não são consideradas livres. A posição do robô é fornecida pela interface;
não há estimativa de pose com ruído, SLAM contínuo ou movimento diagonal.

## 2. Parte 1: busca em largura (BFS)

Após reiniciar o labirinto, o nó obtém a matriz por `/get_map`. A BFS expande os
vértices por distância crescente a partir da origem, usando uma fila FIFO e um
dicionário de predecessores. Quando encontra o alvo, reconstrói o caminho.
Com arestas de custo unitário, a primeira descoberta de cada vértice tem distância
mínima; portanto, a rota retornada minimiza a quantidade de movimentos.

A ordem fixa de vizinhos é cima, baixo, esquerda, direita. Ela resolve empates
de maneira reprodutível. Não é necessário usar Dijkstra, pois todos os pesos
são iguais. A* poderia reduzir expansões com Manhattan, mas BFS é suficiente
para os mapas e simplifica a demonstração de otimalidade.

Tempo: O(V + E). Memória: O(V). No grid, E <= 4V, portanto ambos são O(V).
A execução verifica a confirmação e a posição retornada após cada movimento.
Ausência de caminho é representada por `None`, sem comandos para atravessar paredes.

## 3. Parte 2: exploração online com DFS e retorno

O explorador recebe somente `observe()` e `move(direction)`. Não recebe o CSV,
a matriz completa, a rota da parte 1, as dimensões do grid ou a posição global
do alvo. Embora `MoveCmd` original retorne `target_pos`, esse campo é ignorado.
O alvo é identificado exclusivamente quando aparece nas células adjacentes.

A DFS mantém uma pilha iterativa, um conjunto de visitados e um mapa esparso.
A cada posição, registra os oito sensores. Avança para um vizinho livre ainda
não visitado, ou retorna fisicamente ao pai quando não há vizinho disponível.
O uso de pilha explícita evita estouro de recursão em labirintos grandes.

O simulador encerra os movimentos ao alcançar o alvo. Por isso a DFS registra
o alvo, mas não entra nele. Explora todo o componente da origem no grafo sem
o alvo e retorna à origem. Depois, uma BFS sobre o mapa adquirido encontra a
rota final; o robô a percorre e só então alcança o alvo.

O mapa pode conter regiões desconhecidas, inclusive depois de um alvo que seja
um ponto de articulação. Isso não compromete a entrega: o requisito é que o
mapa seja suficiente para reproduzir a rota, não conhecer regiões irrelevantes.

Para R vértices visitados, a árvore da DFS tem R-1 arestas. Cada uma é percorrida
na ida e na volta: exatamente 2(R-1) movimentos de exploração. A rota final
adiciona d movimentos. Tempo e memória são O(R), mais a BFS no mapa observado.
A trajetória de exploração não é prometida como mínima; a rota final é mínima.

## 4. Por que o mapa é suficiente

Seja P um caminho mínimo da origem s ao alvo t no grafo original G. Como todos
os custos são positivos, P é simples: repetir vértices criaria um ciclo removível.
Logo, P só visita t no último passo. Todos os seus vértices anteriores a t
pertencem ao componente C de s em G sem t.

A DFS visita todo C. O predecessor de t em P pertence a C e observa t por um
sensor cardinal. Assim, o mapa adquirido contém todos os vértices e arestas
de P. Ele não inventa nenhuma passagem: suas arestas são um subconjunto das
arestas reais. Portanto, a distância no mapa adquirido não pode ser menor
que a real e não pode ser maior que o comprimento de P. As distâncias são iguais.

Todos os caminhos mínimos possíveis para t estão preservados. Com a mesma
ordem determinística de vizinhos, as duas BFS reproduzem também a mesma
sequência de células. O programa verifica sequência e custo separadamente.
Se t for inacessível, nenhum caminho é fabricado e a exploração termina.

## 5. Integração ROS 2 e ajustes do simulador

O novo pacote `cg_navigation` contém o algoritmo puro e um adaptador ROS 2.
O executável `navigate` aceita `part:=1`, `part:=2` e `part:=both` como strings.
No modo `both`, a execução ocorre na ordem: reset, parte 1, reset do mesmo
mapa, parte 2, comparação. Nenhum reset aleatório é solicitado.

Foi acrescentado `/observe` com a interface `Observe.srv`. A resposta reúne
posição atual e os mesmos oito sensores locais já existentes no tópico,
sem mapa completo nem posição do alvo. É uma extensão de sincronização:
evita associar uma mensagem antiga da fila do tópico à posição posterior
a um movimento. O tópico original continua disponível.

`ready` indica se o reset solicitado já foi efetivado pela thread gráfica.
O cliente espera esse estado antes de usar observações. Serviços têm tempo
limite e erros interrompem a execução. Um timeout de movimento não é repetido
automaticamente, pois a primeira chamada pode ter sido aplicada pelo servidor.

Foram adicionadas verificações de borda para impedir índices negativos e
acesso fora da matriz, além de rejeição a direções inválidas e exclusão mútua
entre reset e movimento por serviço. Não use teleop ou teclas de movimento
simultaneamente ao nó autônomo. O cenário pressupõe labirinto estático.

## 6. Resultados efetivamente executados

Validação local em 23/11/2026: algoritmos Python executados com CPython 3.9.7
embutido no GDB instalado no computador. Não houve execução do ROS 2 ou da
janela Pygame nesta sessão. Os arquivos em `results/offline` são evidências
do modelo discreto offline, não registros de uma execução ROS.

| Mapa | Custo parte 1 | Custo parte 2 | Mesma sequência | Movimentos de exploração |
|---|---:|---:|:---:|---:|
| 1 | 102 | 102 | Sim | 780 |
| 2 | 102 | 102 | Sim | 780 |
| 3 | 192 | 192 | Sim | 780 |
| 4 | 114 | 114 | Sim | 780 |
| 5 | 204 | 204 | Sim | 780 |
| 6 | 110 | 110 | Sim | 780 |
| 7 | 96 | 96 | Sim | 780 |
| 8 | 164 | 164 | Sim | 780 |
| 9 | 190 | 190 | Sim | 780 |
| 10 | 48 | 48 | Sim | 780 |
| test | 25 | 25 | Sim | 1454 |

A suíte original possui 16 testes, incluindo 300 grids aleatórios com sementes fixas,
comparação com um cálculo de distância independente, becos, ciclos, empates,
alvo adjacente, alvo como articulação, alvo inalcançável, limites abertos,
diagonal bloqueada, mapa inválido e falhas de movimento.

Cada mapa gera JSON com as duas rotas completas e métricas, CSV do mapa
observado e SVG da rota. No SVG: azul = origem, vermelho = alvo, verde = rota,
cinza claro = livre, escuro = parede e cinza médio = desconhecido.
O CSV usa coordenadas locais da caixa delimitadora; o JSON preserva as
coordenadas absolutas de todas as células, inclusive observações de borda.

## 7. Validação ROS 2 neste repositório em 25/11/2026

Nesta integração, foi possível acessar o Ubuntu 24.04 no WSL e executar ROS 2
Jazzy com Python 3.12.3 e Pygame 2.5.2. Os três pacotes compilaram com
`colcon build --symlink-install`. A suíte atual tem 20 testes aprovados: os
16 originais e quatro regressões para seleção de mapa e direção inválida.

O script `scripts/validate_ros.sh` executou os 11 mapas da tabela com o
simulador e o navegador em processos separados, usando os serviços ROS reais.
Todos retornaram `same_route=True`, e as rotas também foram comparadas com
os resultados offline do mapa correspondente. Os custos e os movimentos de
exploração coincidiram com a tabela. A parte 2 usou somente observações locais
e comandos de movimento durante a exploração.

A execução real revelou e permitiu corrigir o conflito com a propriedade
`Node.clients` e a serialização de coordenadas NumPy para JSON. Também foram
corrigidos o tratamento do separador `--` na seleção de mapa e a sincronização
de leituras, desenho e teclado com movimentos e resets.

As evidências estão em `results/ros/mapa_<nome>/`: `part1.json`, `part2.json`,
`part2_mapped.csv` e `part2.svg`. O resumo comparativo está em
`results/ros/summary.json`; os registros de compilação e testes estão em
`results/validation/`.

O Pygame foi executado com `SDL_VIDEODRIVER=dummy`, sem janela visível. Isso
valida a integração e a navegação, mas não constitui inspeção visual da GUI.
O roteiro de demonstração com janela permanece no README.


## Referências

- Enunciado: Desafio de navegação autônoma - Atividade ponderada, fornecido em PDF.
- Simulador original: https://github.com/rmnicola/culling_games
- Código do simulador adaptado neste projeto; licença MIT preservada.
- ROS 2 Jazzy: https://docs.ros.org/en/jazzy/

