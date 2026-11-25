"""ROS 2 adapter. Global map access is isolated to Part 1."""

import time
from pathlib import Path

import rclpy
from rclpy.node import Node
from cg_interfaces.srv import GetMap, MoveCmd, Observe, Reset

from .core import SENSORS, bfs, explore, follow, parse_grid
from .offline import SensorPort, save_result


class Navigator(Node):
    def __init__(self):
        super().__init__('autonomous_navigation')
        self.declare_parameter('part', 'both')
        self.declare_parameter('output', 'results/ros')
        self.declare_parameter('timeout', 15.0)
        self.timeout = float(self.get_parameter('timeout').value)
        if self.timeout <= 0:
            raise ValueError('timeout must be positive')
        self.service_clients = {srv: self.create_client(srv, name) for srv, name in (
            (Observe, '/observe'), (MoveCmd, '/move_command'), (Reset, '/reset'))}

    def call(self, kind, request):
        client = self.service_clients[kind]
        if not client.wait_for_service(timeout_sec=self.timeout):
            raise RuntimeError(f'Service unavailable: {client.srv_name}')
        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=self.timeout)
        if not future.done():
            future.cancel()
            raise TimeoutError(f'Service timeout: {client.srv_name}; restart before retry')
        response = future.result()
        if response is None:
            raise RuntimeError('Empty service response')
        return response

    def observe(self):
        deadline = time.monotonic() + self.timeout
        while time.monotonic() < deadline:
            response = self.call(Observe, Observe.Request())
            if response.ready:
                return tuple(int(value) for value in response.robot_pos), {
                    name: getattr(response.sensors, name) for name in SENSORS}
            time.sleep(0.02)
        raise TimeoutError('Simulator did not finish reset')

    def reset(self):
        request = Reset.Request()
        request.is_random = False
        request.map_name = ''
        if not self.call(Reset, request).success:
            raise RuntimeError('Reset failed')
        return self.observe()[0]

    def move(self, name):
        request = MoveCmd.Request()
        request.direction = name
        response = self.call(MoveCmd, request)
        if not response.success:
            raise RuntimeError(f'Movement rejected: {name}')
        # target_pos deliberately ignored: it leaks global target coordinates.
        return tuple(int(value) for value in response.robot_pos)

    def run(self):
        part = str(self.get_parameter('part').value)
        if part not in {'1', '2', 'both'}:
            raise ValueError('part must be 1, 2 or both')
        output = Path(str(self.get_parameter('output').value))
        output.mkdir(parents=True, exist_ok=True)
        reference = None
        if part in {'1', 'both'}:
            self.reset()
            self.service_clients[GetMap] = self.create_client(GetMap, '/get_map')
            response = self.call(GetMap, GetMap.Request())
            height, width = response.occupancy_grid_shape
            flat = response.occupancy_grid_flattened
            if len(flat) != height * width:
                raise ValueError('Inconsistent map dimensions')
            cells, start, goal = parse_grid([list(flat[r*width:(r+1)*width]) for r in range(height)])
            reference = bfs(cells, start, goal)
            if reference:
                follow(self, reference)
            import json
            (output / 'part1.json').write_text(json.dumps({
                'execution': 'ros2', 'path': reference,
                'cost': len(reference)-1 if reference else None}, indent=2), encoding='utf-8')
            self.get_logger().info(f'Part 1: cost={len(reference)-1 if reference else None}')
        if part in {'2', 'both'}:
            self.reset()
            # No reference route or map is passed into exploration.
            mapped = explore(SensorPort(self.observe, self.move))
            if mapped['path']:
                follow(self, mapped['path'])
            result = save_result(output, 'part2', reference, mapped, 'ros2')
            if part == '2':
                # A standalone run has no Part 1 baseline; do not claim comparison.
                result['same_route'] = None
                result['same_cost'] = None
                import json
                (output / 'part2.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
            elif reference != mapped['path']:
                raise AssertionError('Part 2 failed to reproduce the Part 1 route')
            self.get_logger().info(f'Part 2: cost={result["part2_cost"]}; same_route={result["same_route"]}')
        self.get_logger().info(f'Finished. Evidence: {output.resolve()}')


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = Navigator()
        node.run()
    except Exception as exc:
        if node is not None:
            node.get_logger().error(str(exc))
        raise
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
