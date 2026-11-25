"""Run with: python -m unittest discover -s tests -v."""
import random
import sys
import unittest
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src' / 'cg_navigation'))
from cg_navigation.core import bfs, explore, follow, parse_grid
from cg_navigation.offline import LocalWorld, SensorPort


def grid(*rows):
    return [list(row) for row in rows]


def independent_distance(board, start, goal):
    """Independent reference using a distance matrix, not production BFS."""
    distance = [[-1] * len(board[0]) for _ in board]
    distance[start[0]][start[1]] = 0
    queue = deque([start])
    while queue:
        r, c = queue.popleft()
        if (r, c) == goal:
            return distance[r][c]
        for nr, nc in ((r+1,c), (r-1,c), (r,c+1), (r,c-1)):
            if (0 <= nr < len(board) and 0 <= nc < len(board[0])
                    and board[nr][nc] != 'b' and distance[nr][nc] < 0):
                distance[nr][nc] = distance[r][c] + 1
                queue.append((nr, nc))
    return None


class NavigationTests(unittest.TestCase):
    def check_case(self, board):
        world = LocalWorld(board)
        expected = bfs(world.cells, world.start, world.goal)
        oracle = independent_distance(board, world.start, world.goal)
        self.assertEqual(len(expected)-1 if expected else None, oracle)
        mapped = explore(SensorPort(world.observe, world.move))
        self.assertEqual(world.position, world.start)
        self.assertEqual(mapped['exploration_steps'], 2 * (mapped['visited'] - 1))
        self.assertEqual(mapped['path'], expected)
        for point, value in mapped['cells'].items():
            real = world.cells.get(point, 'b')
            self.assertEqual(value, 'f' if real == 'r' else real)
        if expected:
            follow(world, mapped['path'])
            self.assertEqual(world.position, world.goal)

    def test_corridor(self):
        self.check_case(grid('bbbbbb', 'brfftb', 'bbbbbb'))

    def test_adjacent_target(self):
        self.check_case(grid('rt'))

    def test_target_is_articulation(self):
        self.check_case(grid('rftfff'))

    def test_unreachable(self):
        self.check_case(grid('rbft'))

    def test_diagonal_is_not_move(self):
        self.check_case(grid('rb', 'bt'))

    def test_cycle_and_ties(self):
        self.check_case(grid('rfff', 'fbff', 'ffft'))

    def test_open_boundaries(self):
        self.check_case(grid('rff', 'fft'))

    def test_dead_ends(self):
        self.check_case(grid('bbbbbbb', 'brffffb', 'bfbfbbb', 'bfbfftb', 'bbbbbbb'))

    def test_invalid_maps(self):
        for board in ([], [[]], grid('rrt'), grid('rff'), grid('rtx'), grid('rf', 't')):
            with self.subTest(board=board), self.assertRaises(ValueError):
                parse_grid(board)

    def test_start_equals_goal(self):
        self.assertEqual(bfs({(0, 0): 'f'}, (0, 0), (0, 0)), [(0, 0)])

    def test_unknown_is_not_free(self):
        self.assertIsNone(bfs({(0,0): 'f', (0,2): 't'}, (0,0), (0,2)))

    def test_failed_motion_detected(self):
        world = LocalWorld(grid('rfft'))
        with self.assertRaises(RuntimeError):
            explore(SensorPort(world.observe, lambda direction: world.position))

    def test_wrong_route_origin(self):
        with self.assertRaises(RuntimeError):
            follow(LocalWorld(grid('rft')), [(0,1), (0,2)])

    def test_300_seeded_random_grids(self):
        for seed in range(300):
            rng = random.Random(seed)
            height, width = rng.randint(2, 15), rng.randint(2, 15)
            board = [['b' if rng.random() < .3 else 'f' for _ in range(width)]
                     for _ in range(height)]
            board[0][0], board[-1][-1] = 'r', 't'
            with self.subTest(seed=seed):
                self.check_case(board)


if __name__ == '__main__':
    unittest.main()
