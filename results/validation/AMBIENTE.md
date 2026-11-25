# Escopo da validação

## Validação atual neste repositório — 25/11/2026

- Ubuntu 24.04 no WSL, Python 3.12.3, ROS 2 Jazzy, Pygame 2.5.2.
- `cg_interfaces`, `cg` e `cg_navigation`: compilação aprovada pelo colcon.
- 20 testes aprovados, incluindo os 300 grids aleatórios dos testes originais.
- Sintaxe Python verificada com `compileall`.
- 11 mapas executados offline e também pelo simulador com serviços ROS reais.
- Todas as rotas ROS das partes 1 e 2 coincidiram entre si e com o mapa offline
  correspondente; ver `../ros/summary.json`.
- Pygame executado com driver SDL `dummy`: não houve inspeção de janela visível.
- Comando reproduzível: `bash scripts/validate_ros.sh 1.csv 2.csv 3.csv 4.csv 5.csv 6.csv 7.csv 8.csv 9.csv 10.csv test.csv`.
- Registros atuais: `tests_atual.txt`, `offline_atual.txt`, `build_atual.txt`
  e `ros_atual.txt`.

Os registros abaixo descrevem as validações anteriores que vieram no ZIP.
As limitações anteriores de acesso ao WSL foram superadas nesta execução.

## Histórico do pacote recebido

Data: 23/11/2026.

- Interpretador efetivamente usado: CPython 3.9.7 embutido no GDB do CodeBlocks.
- 16 testes passaram; um deles executa 300 grids aleatórios reproduzíveis.
- Dois testes exercitam a classe Robot original com um backend de matriz sem GUI.
- Os 11 CSV originais foram processados; todas as rotas/custos coincidiram.
- Compilação de sintaxe Python dos pacotes cg e cg_navigation aprovada.
- ROS 2, colcon e Pygame gráfico: não executados nesta sessão.
- Motivo: WSL retornou acesso negado no ambiente disponível.

`tests.txt` registra a execução efetiva. A saída offline está em
`../offline/summary.json` e nos arquivos por mapa. Não há registros ROS
pré-fabricados. Siga o README para produzi-los no ambiente ROS real.

## Verificação do pacote reduzido em 25/11/2026

Os 16 testes, incluindo 300 grids aleatórios, passaram novamente em Python 3.12.
Os 11 mapas originais reproduziram exatamente as mesmas rotas nas duas partes.
A sintaxe Python foi verificada após a remoção do editor e dos exemplos.
A integração ROS 2/Pygame permanece sem execução completa nesta sessão.
