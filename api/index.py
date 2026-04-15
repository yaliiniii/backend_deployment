import os
import sys

# Add the parent directory to sys.path so we can import from the root of the backend folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
