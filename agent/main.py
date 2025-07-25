#!/usr/bin/env python
"""
Convenience script to run the agent from within the agent directory.
This allows running with just: python run.py
"""

import sys
import os

# Add project root to Python path so agent module can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import runpy

if __name__ == "__main__":
    # Delegate execution to the agent package's __main__.py
    runpy.run_module('agent', run_name="__main__", alter_sys=True)
