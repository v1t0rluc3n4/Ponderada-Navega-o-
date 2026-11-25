"""Reproducible offline harness; not a substitute for ROS integration tests."""

import argparse
import csv
import json
from pathlib import Path

from .core import SENSORS, MOVES, FREE, add, bfs, explore, follow, parse_grid


class LocalWorld:
    def __init__(self, grid):
        self.cells, self.start, self.goal = parse_grid(grid)
        self.position = self.start
        self.moves = 0

    def observe(self):
        return self.position, {name: self.cells.get(add(self.position, delta), 'b')
                               for name, delta in SENSORS.items()}

    def move(self, name):
        if self.position == self.goal:
            raise RuntimeError('Simulator locks movement after victory')
        next_cell = add(self.position, MOVES[name])
        if self.cells.get(next_cell) not in FREE:
            raise RuntimeError('Collision')
        self.position = next_cell
        self.moves += 1
        return self.position


class SensorPort:
    """Only the two permitted operations are passed to the explorer."""
    def __init__(self, observe, move):
        self.observe = observe
        self.move = move


def save_result(output, name, reference, mapped, mode):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    path = mapped['path']
    result = {
        'map': name, 'execution': mode,
        'part1_path': reference, 'part2_path': path,
        'part1_cost': len(reference) - 1 if reference else None,
        'part2_cost': len(path) - 1 if path else None,
        'same_route': reference == path,
        'same_cost': (len(reference) if reference else None) == (len(path) if path else None),
        'reachable': path is not None,
        'visited_cells': mapped['visited'],
        'exploration_steps': mapped['exploration_steps'],
        'start': mapped['start'], 'goal_detected': mapped['goal'],
        'known_cells': [{'row': p[0], 'col': p[1], 'value': v}
                        for p, v in sorted(mapped['cells'].items())],
    }
    (output / f'{name}.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    cells = mapped['cells']
    rows = range(min(p[0] for p in cells), max(p[0] for p in cells) + 1)
    cols = range(min(p[1] for p in cells), max(p[1] for p in cells) + 1)
    with (output / f'{name}_mapped.csv').open('w', newline='', encoding='utf-8') as stream:
        csv.writer(stream).writerows([[cells.get((r, c), '?') for c in cols] for r in rows])
    # SVG has no runtime dependencies. Gray cells are unknown, not free.
    route = set(path or [])
    colors = {'b': '#172033', 'f': '#f3f5f8', 't': '#ef4444', '?': '#8b95a5'}
    size = 18
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{len(cols)*size}" height="{len(rows)*size}" viewBox="0 0 {len(cols)*size} {len(rows)*size}">']
    for r in rows:
        for c in cols:
            p = (r, c)
            color = '#34d399' if p in route else colors.get(cells.get(p, '?'), '#f3f5f8')
            if p == mapped['goal']:
                color = '#ef4444'
            if p == mapped['start']:
                color = '#3b82f6'
            svg.append(f'<rect x="{(c-cols.start)*size}" y="{(r-rows.start)*size}" width="18" height="18" fill="{color}" stroke="#cbd5e1" stroke-width="0.3"/>')
    svg.append('</svg>')
    (output / f'{name}.svg').write_text('\n'.join(svg), encoding='utf-8')
    return result


def run_case(grid, output, name):
    world = LocalWorld(grid)
    reference = bfs(world.cells, world.start, world.goal)
    if reference:
        follow(world, reference)
    world = LocalWorld(grid)
    mapped = explore(SensorPort(world.observe, world.move))
    assert world.position == world.start
    assert mapped['path'] == reference, f'Route mismatch: {name}'
    if mapped['path']:
        follow(world, mapped['path'])
        assert world.position == world.goal
    return save_result(output, name, reference, mapped, 'offline_python')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--maps', default='src/cg/maps')
    parser.add_argument('--output', default='results/offline')
    args = parser.parse_args()
    paths = sorted(Path(args.maps).glob('*.csv'))
    if not paths:
        parser.error('No CSV maps found')
    summary = []
    for path in paths:
        with path.open(encoding='utf-8-sig', newline='') as stream:
            grid = list(csv.reader(stream))
        result = run_case(grid, args.output, path.stem)
        summary.append({key: result[key] for key in (
            'map', 'part1_cost', 'part2_cost', 'same_route', 'reachable',
            'visited_cells', 'exploration_steps')})
        print(json.dumps(summary[-1]))
    Path(args.output, 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
