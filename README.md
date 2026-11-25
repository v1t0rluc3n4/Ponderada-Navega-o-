# Navegação autônoma - Ponderada

**Vitor Lopes Lucena | RA A2025.1A.0278 | Entrega: 27/11/2026**

Solução das partes 1 e 2 integrada ao simulador ROS 2 Culling Games.

- **Parte 1:** BFS no mapa conhecido encontra o menor número de movimentos.
- **Parte 2:** DFS com sensores locais constrói o mapa, volta à origem e usa
  BFS para reproduzir a mesma rota, sem consultar `/get_map` na exploração.
- **Comprovação:** 11 mapas originais com rotas idênticas nas duas partes;
  20 testes passando, incluindo 300 grids aleatórios com sementes fixas.

## Comece aqui

Os arquivos do ZIP foram integrados diretamente neste repositório. Execute os
comandos na pasta que contém `src`, `tests`, `validate.py` e este README.

O pacote contém somente o simulador, as interfaces, a navegação autônoma,
os mapas, as dependências visuais, os testes e a documentação/evidências da
entrega. A pasta `lobotomy_kaisen` é mantida porque o simulador carrega essas
imagens ao iniciar. Editor de mapas, teleoperação, exemplos avulsos e material
de estudo não fazem parte deste pacote.

**Validado em 25/11/2026:** os três pacotes compilaram no ROS 2 Jazzy e os
11 mapas passaram também pela execução real dos serviços ROS com Pygame
em modo sem janela no Ubuntu 24.04/WSL. As rotas das duas partes coincidiram
entre si e com as referências offline. Veja [as evidências ROS](results/ros/summary.json).
A aparência da janela não foi inspecionada; use a demonstração abaixo para
apresentar visualmente o trabalho.

## 1. Testar sem ROS (Windows, Linux ou macOS)

Pré-requisito: Python 3.9 ou superior. Não requer bibliotecas externas.
No terminal aberto na raiz:

```bash
python -m unittest discover -s tests -v
python validate.py
```

No Ubuntu, use `python3` se o comando `python` não existir.
Os resultados ficam em `results/offline/`:

- `summary.json`: custos, igualdade das rotas e passos da exploração.
- `<mapa>.json`: rotas completas e todas as células observadas.
- `<mapa>_mapped.csv`: mapa descoberto; `?` significa desconhecido.
- `<mapa>.svg`: imagem do mapa e da rota, abrível no navegador.

A validação offline usa o mesmo núcleo de algoritmos do nó ROS, com um
adaptador discreto de sensores/movimentos; não simula transporte ROS ou GUI.

## 2. Compilar o projeto ROS 2

Ambiente indicado: Ubuntu 24.04 com ROS 2 Jazzy instalado e interface gráfica
(ou WSL2 com WSLg funcionando). O projeto precisa ser executado dentro do Ubuntu,
não no PowerShell/Git Bash do Windows. Instalação oficial do ROS:
https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html

Abra a raiz do projeto no terminal Ubuntu. Nesta máquina, o caminho no WSL é:

```bash
cd /mnt/c/Users/vitor/.vscode/Ponderada-Navega-o-
```

Se extraiu o ZIP em outro local, navegue até a pasta que contém `src`.
Com ROS instalado:

```bash
source /opt/ros/jazzy/setup.bash
sudo apt update
sudo apt install -y python3-pygame python3-colcon-common-extensions python3-rosdep
rosdep update
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

Caso `rosdep update` informe que o rosdep não foi inicializado, execute uma vez
`sudo rosdep init` e repita `rosdep update`. Não inicialize novamente se já existir.
Recompile depois de qualquer alteração nas interfaces `.srv`.

## 3. Demonstrar ambas as partes

### Validação automática no WSL/Ubuntu

Com as dependências instaladas, este comando compila os pacotes, executa os
testes e navega nos 11 mapas usando ROS 2 real e Pygame sem abrir uma janela:

```bash
bash scripts/validate_ros.sh 1.csv 2.csv 3.csv 4.csv 5.csv 6.csv 7.csv 8.csv 9.csv 10.csv test.csv
```

Sem argumentos, o script valida somente `1.csv`. O resumo fica em
`results/ros/summary.json`, com comparação entre as rotas ROS e offline.
Os registros dos testes e da compilação ficam em `results/validation/`.
O script usa o domínio ROS 151 para separar a validação da execução manual.

### Demonstração com janela

**Terminal 1**, na raiz:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run cg maze -- --map 1.csv
```

**Terminal 2**, também na raiz:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run cg_navigation navigate --ros-args -p part:=both -p output:=results/ros/mapa_1
```

A execução reinicia o mapa, realiza a parte 1, reinicia o mesmo mapa, explora
sem entrar no alvo, retorna à origem e executa a rota da parte 2. Ao terminar,
o log deve mostrar `same_route=True`. Verifique também os arquivos JSON.

Não execute teleop nem pressione teclas de movimento durante a demonstração.
Não solicite reset ou troque de mapa enquanto o nó estiver navegando.

Para testar outro mapa, encerre o simulador com Ctrl+C, abra novamente com
`--map 2.csv` (ou outro nome) e use uma pasta de saída diferente.

### Executar cada parte separadamente

Force `part` como string para os valores numéricos:

```bash
ros2 run cg_navigation navigate --ros-args -p "part:='1'" -p output:=results/ros/parte1
ros2 run cg_navigation navigate --ros-args -p "part:='2'" -p output:=results/ros/parte2
```

A parte 2 isolada não consulta nem compara com a parte 1; os campos de
comparação ficam `null`. Use `both` para obter a comprovação conjunta.

### Se ocorrer erro

- `/observe` indisponível: recompile todo o workspace e faça `source` nos dois
  terminais; essa interface é nova.
- Janela não abre: confira o ambiente gráfico/WSLg e o pacote pygame.
- Movimento rejeitado/posição divergente: pare qualquer teleop, reinicie
  o simulador e execute novamente.
- Timeout: confira se a janela não foi fechada e se o simulador está respondendo.
  Não repita comandos de movimento manualmente para tentar corrigir a posição.
- `Package not found`: confirme a raiz correta e `source install/setup.bash`.

## 4. Documentação

- [Relatório técnico e prova de correção](docs/RELATORIO.md)
- [Inventário dos arquivos alterados](docs/ALTERACOES.md)
- [Resumo dos resultados offline](results/offline/summary.json)
- [Resumo dos resultados ROS 2](results/ros/summary.json)
- [Ambiente e registros de validação](results/validation/AMBIENTE.md)

A otimização se refere ao **caminho final**, e não ao custo de explorar.
O alvo bloqueia movimentos após a vitória no simulador. A exploração evita
entrá-lo até concluir o mapeamento necessário. A justificativa de correção está no relatório.

## 5. Publicar e entregar

1. Crie seu repositório no GitHub, público ou compartilhado com o professor.
2. Envie **todo o conteúdo desta pasta**, incluindo `src`, `docs`, `tests`,
   `results` e as imagens originais. Não envie apenas o ZIP.
3. Depois da demonstração ROS, adicione também os resultados em `results/ros`.
4. Confira o README e a acessibilidade do link (janela anônima se for público).
5. Envie **o link do repositório** na plataforma da atividade até 27/11.

Pelo terminal, após criar um repositório vazio, sem README automático:

```bash
git init
git add .
git commit -m "feat: navegação BFS e mapeamento autônomo por sensores"
git branch -M main
git remote add origin URL_DO_SEU_REPOSITORIO
git push -u origin main
```

Substitua `URL_DO_SEU_REPOSITORIO` pela URL real que você criou.

Este pacote reúne as duas partes práticas. O relatório explica a solução e
sua validação. O material de estudo foi separado em outro ZIP.

## Créditos e licença

Simulador de Rodrigo Nicola: https://github.com/rmnicola/culling_games.
Licença MIT original preservada. A solução acrescenta `cg_navigation` e
ajustes de sincronização/limites documentados em `docs/ALTERACOES.md`.

