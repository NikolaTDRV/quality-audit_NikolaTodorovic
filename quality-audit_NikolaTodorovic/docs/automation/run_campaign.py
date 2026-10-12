# -*- coding: utf-8 -*-
import sys
from core import run_all
import tests_a  # noqa
try:
    import tests_b  # noqa
    import tests_c  # noqa
    import tests_d  # noqa
    import tests_e  # noqa
except ImportError:
    pass
if __name__ == "__main__":
    run_all(only=set(sys.argv[1:]) or None)
