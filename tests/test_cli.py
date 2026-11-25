"""Regressions for the documented simulator invocation."""
import contextlib
import io
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src' / 'cg'))
from cg.cli import parse_game_args


class CliTests(unittest.TestCase):
    def test_explicit_map_with_and_without_separator(self):
        for argv in (['--map', '1.csv'], ['--', '--map', '1.csv']):
            self.assertEqual(parse_game_args(argv).map, '1.csv')

    def test_generate_with_separator(self):
        self.assertTrue(parse_game_args(['--', '--generate']).generate)

    def test_invalid_options_do_not_silently_select_random_map(self):
        for argv in (['--mp', '1.csv'], ['--map', '1.csv', '--generate']):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                parse_game_args(argv)
