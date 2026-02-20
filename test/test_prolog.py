import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from prolog import PrologInterface

def test_prolog_connection():
    interface = PrologInterface()
    assert interface is not None