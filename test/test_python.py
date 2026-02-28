import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from llms.llm import LLMInterface
from main import main
from Orchestrator import Orchestrator

def test_python_module():
    assert main is not None
    assert LLMInterface is not None
    assert Orchestrator is not None