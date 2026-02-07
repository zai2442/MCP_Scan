import logging
from typing import Dict, Any, List, Optional
from mcp_scan.command_executor import CommandExecutor

logger = logging.getLogger(__name__)

def run_nuclei(target: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Execute Nuclei vulnerability scan.
    
    Args:
        target: URL (http/https).
        tags: List of tags e.g. ["cve", "misconfig"].
        
    Returns:
        Scan results.
    """
    if not target:
        return {"error": "Target is required", "success": False}
        
    if ";" in target or "|" in target:
        return {"error": "Invalid target format", "success": False}
        
    command_parts = ["nuclei", "-target", target]
    
    if tags:
        tags_str = ",".join(tags)
        if all(c.isalnum() or c in "-_," for c in tags_str):
            command_parts.append(f"-tags {tags_str}")
        else:
             return {"error": "Invalid tags format", "success": False}
             
    # Rate limit per spec: 50 requests/second
    command_parts.append("-rate-limit 50")
    
    full_command = " ".join(command_parts)
    
    logger.info(f"Running nuclei: {full_command}")
    executor = CommandExecutor(full_command, timeout=600) # Nuclei might take longer
    result = executor.execute()
    
    result["success"] = result["return_code"] == 0
    return result
