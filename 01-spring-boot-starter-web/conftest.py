import os
import sys

# Make the `main` module importable when pytest runs from this folder.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
