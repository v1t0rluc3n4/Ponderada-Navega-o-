# Organização do pacote de entrega

## Código necessário às partes 1 e 2

- `src/cg/`: simulador Pygame, mapas e comando `maze`.
- `src/cg_interfaces/`: mensagens e serviços ROS, incluindo `Observe.srv`.
- `src/cg_navigation/`: BFS, exploração DFS, integração ROS e validação offline.
- `lobotomy_kaisen/`: imagens carregadas pelo simulador; dependência preservada.

## Execução e comprovação

- `README.md`: instalação, execução, validação e publicação.
- `validate.py` e `tests/`: validação reproduzível.
- `results/offline/`: rotas, métricas e mapas descobertos dos 11 labirintos.
- `results/validation/`: registros de testes e limites da validação realizada.
- `docs/RELATORIO.md`: explicação técnica e justificativa de correção.
- `LICENSE`, licenças dos pacotes e `.gitignore`: licença e organização do repositório.

## Ajustes em relação ao simulador original

- `Game.py`: serviço de observação local sincronizada e validação do movimento.
- `Maze.py` e `Utils/Finders.py`: verificações dos limites da matriz.
- `cg_interfaces/CMakeLists.txt`: registro da nova interface Observe.
- `cg/package.xml`: declaração de dependências.
- `cg/main.py` e `cg/setup.py`: remoção do import e dos comandos de editor/exemplo,
  pois esses arquivos foram excluídos do pacote reduzido.

## Itens separados ou excluídos

O guia para a prova está somente no ZIP de estudos.
Foram excluídos editor de mapas, exemplo `teste.py`, pacote de teleoperação,
gerador avulso (a função interna usada pelo simulador permanece), README
duplicado, workflow opcional e testes de estilo originais.
As licenças e todos os recursos usados na execução das duas partes permanecem.

## Integração neste repositório em 25/11/2026

- Conteúdo do ZIP integrado na raiz do workspace, com as licenças preservadas.
- `cg/cli.py`: leitura explícita dos argumentos, aceitando o separador `--`
  usado no README, sem ignorar a escolha do mapa ou opções inválidas.
- `Robot.py`: direções inválidas são rejeitadas sem alterar a matriz.
- `Game.py`: snapshots de mapa e sensores protegidos pelo mesmo lock dos
  movimentos; teclado respeita vitória e reset; desenho sincronizado e limitado
  a 60 quadros por segundo.
- `ros_node.py`: evidência da parte 1 gravada somente após concluir a rota.
  Dicionário de serviços renomeado para não sobrescrever a propriedade
  somente leitura `Node.clients`, que impedia a inicialização no ROS 2 Jazzy.
  Coordenadas recebidas do ROS são convertidas para `int` nativo, permitindo
  salvar os resultados JSON quando a interface fornece escalares NumPy.
- `main.py`: encerramento normal da thread ROS tratado sem traceback.
- Quatro testes de regressão adicionados, totalizando 20 testes.
- `scripts/validate_ros.sh`: compilação e validação reproduzível usando serviços
  ROS reais e Pygame com driver SDL sem janela.

Não houve publicação remota. Consulte `results/validation/AMBIENTE.md` para
o registro das execuções feitas neste workspace.
