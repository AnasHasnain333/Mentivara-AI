import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import pytest


@pytest.fixture(scope="session", autouse=True)
def trained_model():
    """Make sure a model exists (trains in a few seconds if it does not)."""
    from utils import predictor
    if not predictor.model_exists():
        import train_model
        train_model.main()
        predictor.reset_cache()
