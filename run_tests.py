import sys
import os
import unittest

# Add src and lib to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, "src"))
# Append vendored 'lib' so site-packages take precedence (avoid shadowing e.g. pydantic)
sys.path.append(os.path.join(project_root, "lib"))

# Force reload of typing_extensions if it was loaded from wrong location
if 'typing_extensions' in sys.modules:
    del sys.modules['typing_extensions']

if __name__ == "__main__":
    loader = unittest.TestLoader()
    start_dir = os.path.join(project_root, "tests")
    suite = loader.discover(start_dir, pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    sys.exit(not result.wasSuccessful())
