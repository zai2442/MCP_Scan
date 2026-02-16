# MVP P0 Feature Base: Command Executor

This module provides the robust command execution capability required by Feature 2 (Task Scheduling).

## Extracted From
`MCP_kali/MCP-Kali-Server/kali_server.py`

## Usage

```python
from command_executor import CommandExecutor

executor = CommandExecutor("echo 'Hello World'", timeout=10)
result = executor.execute()
print(result)
```

## Compliance with P0
- [x] **Timeouts**: Supports strict timeout enforcement (P0 Requirement: "Timeout: 5 minutes per host").
- [x] **Logging**: Captures both stdout and stderr.
- [x] **Thread Safety**: Uses separate threads for I/O reading to prevent blocking.
