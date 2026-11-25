"""Deterministic BFS and online DFS. No ROS, CSV or simulator dependencies."""

from collections import deque

MOVES = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}
SENSORS = dict(MOVES, up_left=(-1, -1), up_right=(-1, 1),
               down_left=(1, -1), down_right=(1, 1))
FREE = {'f', 'r', 't'}


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def direction(a, b):
    delta = b[0] - a[0], b[1] - a[1]
    for name, offset in MOVES.items():
        if offset == delta:
            return name
    raise ValueError('Movement must connect cardinal neighbors')


def parse_grid(grid):
    if not grid or not grid[0] or any(len(row) != len(grid[0]) for row in grid):
        raise ValueError('Grid must be nonempty and rectangular')
    cells = {(r, c): value for r, row in enumerate(grid) for c, value in enumerate(row)}
    if set(cells.values()) - (FREE | {'b'}):
        raise ValueError('Invalid cell symbol')
    starts = [p for p, v in cells.items() if v == 'r']
    targets = [p for p, v in cells.items() if v == 't']
    if len(starts) != 1 or len(targets) != 1:
        raise ValueError('Expected exactly one robot and one target')
    return cells, starts[0], targets[0]


def bfs(cells, start, goal):
    """Return the minimum-hop path, including endpoints, or None."""
    if cells.get(start) not in FREE or cells.get(goal) not in FREE:
        return None
    queue = deque([start])
    parent = {start: None}
    while queue:
        current = queue.popleft()
        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = parent[current]
            return path[::-1]
        for offset in MOVES.values():
            neighbor = add(current, offset)
            if cells.get(neighbor) in FREE and neighbor not in parent:
                parent[neighbor] = current
                queue.append(neighbor)
    return None


def follow(port, path):
    """Execute a route and verify every movement acknowledgement."""
    if not path:
        raise ValueError('Cannot execute an empty route')
    if port.observe()[0] != path[0]:
        raise RuntimeError('Robot is not at route origin')
    for previous, expected in zip(path, path[1:]):
        actual = port.move(direction(previous, expected))
        if actual != expected:
            raise RuntimeError('Robot position differs from planned route')


def explore(port):
    """Map via local observations only; return to start without entering target.

    The component of start in G minus the target contains every possible
    shortest path prefix. Thus entering the terminal target is unnecessary.
    The port exposes only observe() -> (pose, neighbors) and move(direction).
    """
    start, _ = port.observe()
    cells, visited, stack = {}, {start}, [start]
    goal = None
    steps = 0
    while stack:
        position, nearby = port.observe()
        if position != stack[-1]:
            raise RuntimeError('Unexpected movement; stop teleoperation')
        cells[position] = 'f'
        for name, offset in SENSORS.items():
            value = nearby[name]
            if value not in FREE | {'b'}:
                raise ValueError('Invalid sensor reading')
            neighbor = add(position, offset)
            cells[neighbor] = 'f' if value == 'r' else value
            if value == 't':
                if goal is not None and goal != neighbor:
                    raise ValueError('Multiple targets detected')
                goal = neighbor
        next_cell = next((add(position, delta) for delta in MOVES.values()
                          if cells.get(add(position, delta)) == 'f'
                          and add(position, delta) not in visited), None)
        if next_cell is not None:
            if port.move(direction(position, next_cell)) != next_cell:
                raise RuntimeError('Exploration movement failed')
            visited.add(next_cell)
            stack.append(next_cell)
            steps += 1
        else:
            stack.pop()
            if stack:
                if port.move(direction(position, stack[-1])) != stack[-1]:
                    raise RuntimeError('Backtracking failed')
                steps += 1
    return {'cells': cells, 'start': start, 'goal': goal,
            'visited': len(visited), 'exploration_steps': steps,
            'path': bfs(cells, start, goal) if goal is not None else None}
