# -*- coding: utf-8 -*-
"""Lance la campagne : `python run_campaign.py` (tous les cas) ou `python run_campaign.py TC-RM-04 TC-ERR-06`."""
import sys
from core import run_all
import tests  # noqa: F401  (enregistre les cas)

if __name__ == "__main__":
    run_all(only=set(sys.argv[1:]) or None)
