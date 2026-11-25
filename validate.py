"""Run from repository root: python validate.py."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src' / 'cg_navigation'))

if __name__ == '__main__':
    from cg_navigation.offline import main
    main()
