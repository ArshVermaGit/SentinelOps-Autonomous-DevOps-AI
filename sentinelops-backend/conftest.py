"""
Root conftest.py — ensures 'app' is importable when running pytest.
Author: Arsh Verma
"""

import sys
import os

# Add the backend root to sys.path so 'from app...' works in tests
sys.path.insert(0, os.path.dirname(__file__))
