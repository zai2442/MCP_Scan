# setup.py (放在 d:\PaperDesign\MCP_scan)
from setuptools import setup, find_packages
setup(
    name="mcp_scan",
    version="0.1",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
)