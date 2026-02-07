import logging
import os
import tempfile
from typing import Dict, Any
from mcp_scan.command_executor import CommandExecutor

logger = logging.getLogger(__name__)

ALLOWED_MODULES = [
    "exploit/windows/smb/ms17_010_eternalblue",
    # Add other allowed modules for MVP
]

def run_metasploit(module: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute Metasploit module.
    
    Args:
        module: Metasploit module path.
        options: Dictionary of module options (RHOSTS, LHOST, etc.).
        
    Returns:
        Execution logs and session info.
    """
    if not module:
        return {"error": "Module is required", "success": False}
        
    # Business Rule: Strict whitelist
    if module not in ALLOWED_MODULES:
        return {"error": f"Module {module} is not in the allowed whitelist", "success": False}

    # Generate Resource Script
    try:
        resource_content = f"use {module}\n"
        for key, value in options.items():
            # Basic sanitization for option values
            if ";" in str(value) or "|" in str(value):
                 return {"error": f"Invalid value for option {key}", "success": False}
            resource_content += f"set {key} {value}\n"
        resource_content += "exploit -z\n" # -z to not interact
        
        # Create temp file
        fd, resource_file = tempfile.mkstemp(suffix=".rc", prefix="mcp_msf_")
        with os.fdopen(fd, 'w') as f:
            f.write(resource_content)
            
    except Exception as e:
        return {"error": f"Failed to create resource script: {str(e)}", "success": False}

    command = f"msfconsole -q -r {resource_file}"
    
    logger.info(f"Running metasploit module: {module}")
    executor = CommandExecutor(command, timeout=600)
    result = executor.execute()
    
    # Cleanup
    try:
        os.remove(resource_file)
    except OSError:
        pass

    result["success"] = result["return_code"] == 0
    return result
