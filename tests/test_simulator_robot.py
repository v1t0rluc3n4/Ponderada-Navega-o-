"""Exercise the original Robot with a minimal non-graphical maze backend."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src' / 'cg'))
sys.path.insert(0, str(ROOT / 'src' / 'cg_navigation'))
from cg.Robot import Robot
from cg_navigation.core import explore, follow
from cg_navigation.offline import SensorPort


class MazeBackend:
    def __init__(self, rows):
        self.grid = [list(row) for row in rows]

    def get_occupancy_grid(self):
        return self.grid

    def get_cell(self, pos):
        r, c = pos
        return self.grid[r][c] if 0 <= r < len(self.grid) and 0 <= c < len(self.grid[0]) else 'b'

    def set_cell(self, pos, value):
        self.grid[pos[0]][pos[1]] = value


class SimulatorRobotTests(unittest.TestCase):
    def test_invalid_direction_does_not_modify_grid(self):
        maze = MazeBackend(['rft'])
        robot = Robot(maze)
        self.assertFalse(robot.move('diagonal'))
        self.assertEqual(robot.pos, (0, 0))
        self.assertEqual(maze.grid, [list('rft')])

    def test_actual_robot_exploration_and_replay(self):
        robot = Robot(MazeBackend(['bbbbbb', 'brfftb', 'bffbfb', 'bbbbbb']))

        def move(name):
            if not robot.move(name):
                raise RuntimeError('Blocked')
            return robot.pos

        port = SensorPort(lambda: (robot.pos, robot.check_surroundings()), move)
        result = explore(port)
        self.assertEqual(robot.pos, (1, 1))
        self.assertEqual(result['path'], [(1, 1), (1, 2), (1, 3), (1, 4)])
        follow(port, result['path'])
        self.assertEqual(robot.pos, (1, 4))

    def test_actual_robot_cannot_wrap_grid(self):
        robot = Robot(MazeBackend(['rf', 'ft']))
        self.assertFalse(robot.move('up'))
        self.assertFalse(robot.move('left'))
        self.assertEqual(robot.pos, (0, 0))
