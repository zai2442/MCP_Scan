import sys
import os
import asyncio
import importlib.util

# Add src and lib to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, "src"))
sys.path.insert(0, os.path.join(project_root, "lib"))

# Force reload of typing_extensions
if 'typing_extensions' in sys.modules:
    del sys.modules['typing_extensions']

# Import benchmark module
spec = importlib.util.spec_from_file_location("benchmark", os.path.join(project_root, "tests", "benchmark.py"))
benchmark = importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)

if __name__ == "__main__":
    asyncio.run(benchmark.run_benchmark(50))
