#!/usr/bin/env bash
# Real ROS services and Pygame, using an offscreen SDL display.
set -eo pipefail
cd "$(dirname "$0")/.."
source /opt/ros/jazzy/setup.bash
mkdir -p results/validation
python3 -m unittest discover -s tests -v 2>&1 | tee results/validation/tests_atual.txt
python3 validate.py | tee results/validation/offline_atual.txt
python3 -m compileall -q src tests validate.py
colcon build --symlink-install 2>&1 | tee results/validation/build_atual.txt
source install/setup.bash
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-151}"
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy
server_pid=''
stop_server() {
    if [[ -n "$server_pid" ]]; then
        kill "$server_pid" 2>/dev/null || true
        wait "$server_pid" 2>/dev/null || true
        server_pid=''
    fi
}
trap stop_server EXIT
if [[ $# -eq 0 ]]; then set -- 1.csv; fi
for map in "$@"; do
    name="$(basename "$map" .csv)"
    output="results/ros/mapa_$name"
    mkdir -p "$output"
    install/cg/lib/cg/maze -- --map "$map" > "$output/simulator.log" 2>&1 &
    server_pid=$!
    timeout 180s ros2 run cg_navigation navigate --ros-args \
        -p part:=both -p "output:=$output" 2>&1 | tee "$output/navigation.log"
    stop_server
done
python3 - "$@" <<'PY' | tee results/validation/ros_atual.txt
import json
import sys
from pathlib import Path

summary = []
for filename in sys.argv[1:]:
    name = Path(filename).stem
    output = Path('results/ros') / f'mapa_{name}'
    part1 = json.loads((output / 'part1.json').read_text())
    part2 = json.loads((output / 'part2.json').read_text())
    offline = json.loads(Path(f'results/offline/{name}.json').read_text())
    if not (part1['execution'] == part2['execution'] == 'ros2'
            and part2['same_route'] and part2['same_cost']
            and part1['path'] == part2['part2_path'] == offline['part1_path']):
        raise RuntimeError(f'ROS validation failed for map {name}')
    summary.append({'map': name, 'execution': 'ros2',
                    'part1_cost': part1['cost'], 'part2_cost': part2['part2_cost'],
                    'same_route': True, 'matches_offline': True,
                    'exploration_steps': part2['exploration_steps']})
Path('results/ros/summary.json').write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
PY
