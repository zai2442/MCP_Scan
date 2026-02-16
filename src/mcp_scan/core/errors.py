class MCPScanError(Exception):
    """Base exception for MCP Scan."""
    def __init__(self, message: str, code: str = "E5001"):
        self.message = message
        self.code = code
        super().__init__(f"[{code}] {message}")

class InvalidTargetError(MCPScanError):
    def __init__(self, target: str):
        super().__init__(f"Invalid target format: {target}", "E1001")

class ToolNotFoundError(MCPScanError):
    def __init__(self, tool_name: str):
        super().__init__(f"Tool not found: {tool_name}", "E2001")

class SchedulerError(MCPScanError):
    def __init__(self, message: str):
        super().__init__(message, "E3001")

class ExecutionError(MCPScanError):
    def __init__(self, message: str):
        super().__init__(message, "E4001")
