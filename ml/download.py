"""Fetch the ASSISTments 2009 benchmark split used by DKVMN (Zhang et al., 2017).

    python -m ml.download

Original dataset: https://sites.google.com/site/assistmentsdata/home/2009-2010-assistment-data/skill-builder-data-2009-2010
"""
import urllib.request

from .data import RAW_DIR, SPLITS

BASE = "https://raw.githubusercontent.com/jennyzhang0215/DKVMN/master/data/assist2009_updated/"
FILES = [*SPLITS.values(), "assist2009_updated_skill_mapping.txt"]

if __name__ == "__main__":
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        dest = RAW_DIR / name
        if not dest.exists():
            print(f"downloading {name}")
            urllib.request.urlretrieve(BASE + name, dest)
    print(f"data ready in {RAW_DIR}")
