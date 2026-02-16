import logging
from typing import Dict, Any, Optional
from mcp_scan.command_executor import CommandExecutor

logger = logging.getLogger(__name__)

def run_gobuster(url: str, wordlist: str = "/usr/share/wordlists/dirb/common.txt", threads: int = 10, mode: str = "dir") -> Dict[str, Any]:
    """
    Execute Gobuster scan.
    
    Args:
        url: Target URL.
        wordlist: Path to wordlist.
        threads: Number of threads (default: 10).
        mode: Scan mode (dir, dns, fuzz, vhost). Default: dir.
        
    Returns:
        Scan results.
    """
    if not url:
        return {"error": "URL is required", "success": False}
        
    if ";" in url or "|" in url:
        return {"error": "Invalid URL format", "success": False}

    if mode not in ["dir", "dns", "fuzz", "vhost"]:
        return {"error": f"Invalid mode: {mode}", "success": False}

    command_parts = ["gobuster", mode, "-u", url]
    
    # Wordlist
    # In a real app, validate that wordlist path is safe/allowed
    if ";" in wordlist or "|" in wordlist:
        return {"error": "Invalid wordlist path", "success": False}
    command_parts.append(f"-w {wordlist}")
    
    # Threads
    command_parts.append(f"-t {threads}")
    
    full_command = " ".join(command_parts)
    
    logger.info(f"Running gobuster: {full_command}")
    executor = CommandExecutor(full_command, timeout=600)
    result = executor.execute()
    
    result["success"] = result["return_code"] == 0
    return result
