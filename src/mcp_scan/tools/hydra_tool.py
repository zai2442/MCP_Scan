import logging
from typing import Dict, Any, Optional
from mcp_scan.command_executor import CommandExecutor

logger = logging.getLogger(__name__)

def run_hydra(target: str, service: str, 
              username: Optional[str] = None, user_list: Optional[str] = None, 
              password: Optional[str] = None, pass_list: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute Hydra password cracking.
    
    Args:
        target: IP address.
        service: Service name (ssh, ftp, etc.).
        username: Single username.
        user_list: Path to username list.
        password: Single password.
        pass_list: Path to password list.
        
    Returns:
        Found credentials.
    """
    if not target or not service:
        return {"error": "Target and service are required", "success": False}
        
    if not (username or user_list) or not (password or pass_list):
        return {"error": "Username (or list) and Password (or list) are required", "success": False}

    command_parts = ["hydra"]
    
    # Business Rule: Max limits on thread count
    command_parts.append("-t 4") # Conservative default
    
    if username:
        if ";" in username: return {"error": "Invalid username", "success": False}
        command_parts.append(f"-l {username}")
    elif user_list:
        if ";" in user_list: return {"error": "Invalid user_list path", "success": False}
        command_parts.append(f"-L {user_list}")
        
    if password:
        if ";" in password: return {"error": "Invalid password", "success": False}
        command_parts.append(f"-p {password}")
    elif pass_list:
        if ";" in pass_list: return {"error": "Invalid pass_list path", "success": False}
        command_parts.append(f"-P {pass_list}")
        
    if ";" in target or "|" in target: return {"error": "Invalid target", "success": False}
    if ";" in service or "|" in service: return {"error": "Invalid service", "success": False}
    
    command_parts.append(f"{target} {service}")
    
    full_command = " ".join(command_parts)
    
    logger.info(f"Running hydra: {full_command}")
    executor = CommandExecutor(full_command, timeout=600)
    result = executor.execute()
    
    result["success"] = result["return_code"] == 0
    return result
