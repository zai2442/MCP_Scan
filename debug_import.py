import sys
import os

lib_path = r"d:\PaperDesign\MCP_scan\lib"
sys.path.insert(0, lib_path)

print(f"Path: {sys.path}")
try:
    import pydantic
    print(f"Pydantic version: {pydantic.VERSION}")
    print(f"Pydantic file: {pydantic.__file__}")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")

try:
    import pydantic_core
    print(f"Pydantic Core version: {pydantic_core.__version__}")
except Exception as e:
    print(f"Pydantic Core Error: {e}")
