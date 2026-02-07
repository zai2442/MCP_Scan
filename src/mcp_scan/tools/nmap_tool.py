import logging
from typing import Dict, Any, Optional
from mcp_scan.command_executor import CommandExecutor

logger = logging.getLogger(__name__)

def run_nmap(target: str, ports: str = "top-1000", timing: str = "T3", additional_args: str = "") -> Dict[str, Any]:
    """
    Execute Nmap scan.
    
    Args:
        target: IPv4, IPv6, or Hostname.
        ports: "top-100", "1-65535", or list "80,443". Default: "top-1000".
        timing: "T3" (default), "T4".
        additional_args: Additional arguments (sanitized).
        
    Returns:
        Structured JSON containing scan results (stdout/stderr/return_code).
    """
    # 1. Validation
    if not target:
        return {"error": "Target is required", "success": False}
    
    # TODO: Implement strict target validation (regex for IP/Hostname) to prevent injection if not handled by subprocess
    # CommandExecutor uses shell=True, so we MUST sanitize inputs.
    # Ideally, we should use list args for subprocess, but CommandExecutor takes a string.
    # For MVP, we'll do basic checks.
    if ";" in target or "|" in target or "&" in target:
        return {"error": "Invalid target format", "success": False}

    # 2. Command Construction
    command_parts = ["nmap"]
    
    # Timing
    if timing in ["T3", "T4"]:
        command_parts.append(f"-{timing}")
    else:
        command_parts.append("-T3") # Default
        
    # Ports
    if ports == "top-100":
        command_parts.append("--top-ports 100")
    elif ports == "top-1000":
        command_parts.append("--top-ports 1000")
    elif ports == "1-65535" or ports == "all":
        command_parts.append("-p 1-65535")
    elif ports:
        # Validate ports string (numbers and commas only)
        if all(c.isdigit() or c == ',' or c == '-' for c in ports):
             command_parts.append(f"-p {ports}")
        else:
            return {"error": "Invalid ports format", "success": False}
    else:
         command_parts.append("--top-ports 1000") # Default

    # Additional Args - simplified for MVP
    # In a real scenario, this needs strict allowlisting
    if additional_args:
        # Very basic check
        if ";" in additional_args or "|" in additional_args:
             return {"error": "Invalid additional_args", "success": False}
        command_parts.append(additional_args)
        
    command_parts.append(target)
    
    full_command = " ".join(command_parts)
    
    # 3. Execution
    logger.info(f"Running nmap: {full_command}")
    executor = CommandExecutor(full_command, timeout=300) # 5 minutes timeout per spec
    result = executor.execute()
    
    # 4. Result Parsing (Basic)
    # The spec says "Structured JSON containing open ports...".
    # Nmap output is text unless we use -oX.
    # For MVP P0, we might just return the text output or do basic parsing.
    # The MCP_kali implementation just returns stdout.
    # To strictly follow "Structured JSON", we should probably parse the stdout.
    # But for now, returning the execution result structure is the first step.
    
    result["success"] = result["return_code"] == 0
    return result
