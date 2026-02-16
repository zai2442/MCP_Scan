# MVP P0 Feature Transport: Kali Client

This module provides the HTTP Client abstraction for communicating with remote execution nodes (Feature 1/2).

## Extracted From
`MCP_kali/MCP-Kali-Server/mcp_server.py`

## Usage

```python
from kali_client import KaliToolsClient

client = KaliToolsClient("http://localhost:5000")
result = client.safe_get("health")
```

## Compliance with P0
- [x] **Error Handling**: Wraps requests in try/except blocks.
- [x] **Timeouts**: Supports configurable timeouts (Critical for long-running scans).
- [x] **JSON I/O**: Enforces JSON communication.
