# MCP Scan

**Version**: 1.0.0 (MVP P0)
**Status**: Beta

MCP Scan is a lightweight, modular, AI-orchestrated distributed penetration testing platform that standardizes security tool interactions via the MCP protocol.

## Features (MVP P0)

*   **Comprehensive Tool Support**:
    *   Recon: `nmap`, `gobuster`
    *   Vuln: `nuclei`
    *   Exploit: `sqlmap`, `hydra`, `metasploit`
*   **Intelligent Scheduler**:
    *   Automated DAG execution (e.g., Nmap -> Nuclei).
    *   Async concurrency for high performance.
*   **Developer-Friendly CLI**:
    *   Rich-text output with progress bars and status tables.
    *   Simple commands: `scan start`, `scan status`.

## Installation

1.  **Prerequisites**:
    *   Python 3.8+
    *   Kali Linux tools (`nmap`, `nuclei`, `gobuster`, etc.) installed and in PATH.

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration**:
    *   Ensure `config.yaml` is present (optional for defaults).

## Usage

### Start a Scan
```bash
PYTHONPATH=src python3 -m mcp_scan.cli start --target example.com
```

### Check Status
```bash
PYTHONPATH=src python3 -m mcp_scan.cli status <JOB_ID>
```

### Export Report
```bash
PYTHONPATH=src python3 -m mcp_scan.cli report <JOB_ID> -o <输出文件路径>
```

## Development

### Running Tests
```bash
PYTHONPATH=src python3 run_tests.py
```

### Running Benchmark
```bash
PYTHONPATH=src python3 run_benchmark.py
```

## Architecture
*   `src/mcp_scan/core`: Core logic (Scheduler, Models).
*   `src/mcp_scan/tools`: Tool wrappers.
*   `src/mcp_scan/cli.py`: CLI implementation.
