"""Simulator arguments, after ROS arguments have been removed."""
import argparse


def parse_game_args(argv):
    parser = argparse.ArgumentParser(description='Culling Games Maze Runner')
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument('--map', help='Map filename (e.g. 1.csv)')
    selection.add_argument('--generate', action='store_true',
                           help='Generate a new random maze')
    # Accept both `maze --map 1.csv` and `maze -- --map 1.csv`.
    if argv and argv[0] == '--':
        argv = argv[1:]
    return parser.parse_args(argv)
