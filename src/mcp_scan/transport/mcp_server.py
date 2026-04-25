import asyncio
import logging
from typing import Dict, Any, List

from mcp.server.fastmcp import FastMCP
from mcp_scan.core.scheduler import Scheduler
from mcp_scan.tools.nmap_tool import run_nmap
from mcp_scan.tools.gobuster_tool import run_gobuster
from mcp_scan.tools.nuclei_tool import run_nuclei
from mcp_scan.tools.sqlmap_tool import run_sqlmap
from mcp_scan.tools.hydra_tool import run_hydra
from mcp_scan.core.models import Job, Task, TaskStatus
import json
import uuid

logger = logging.getLogger(__name__)

# Initialize FastMCP Server
mcp = FastMCP("mcp_scan")
scheduler = Scheduler()

@mcp.tool()
async def scan_nmap(target: str, ports: str = "top-1000") -> str:
    """
    Run an Nmap port scan against the target.
    
    Args:
        target: IP address or hostname to scan.
        ports: Ports to scan (e.g., 'top-1000', '80,443', '1-65535').
    """
    logger.info(f"MCP Tool called: scan_nmap({target}, {ports})")
    try:
        # We can either run it directly via the tool wrapper, or dispatch via scheduler.
        # Since tools are blocking in current implementation, we wrap it in a thread.
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None, 
            run_nmap, 
            target, 
            ports, 
            "-sV", 
            False
        )
        if result.get("success"):
            return result.get("stdout", "Success, but no output")
        else:
            return f"Error: {result.get('error')} \n {result.get('stderr')}"
    except Exception as e:
        return f"Tool execution failed: {e}"

@mcp.tool()
async def scan_gobuster(url: str, wordlist: str = "/usr/share/wordlists/dirb/common.txt") -> str:
    """
    Run Gobuster for directory and file enumeration on a web server.
    
    Args:
        url: The base URL to scan (e.g., http://example.com)
        wordlist: Path to the wordlist file.
    """
    logger.info(f"MCP Tool called: scan_gobuster({url})")
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None, 
            run_gobuster, 
            url, 
            wordlist,
            False
        )
        if result.get("success"):
            return result.get("stdout", "Success, but no output")
        else:
            return f"Error: {result.get('error')} \n {result.get('stderr')}"
    except Exception as e:
        return f"Tool execution failed: {e}"

@mcp.tool()
async def scan_nuclei(target: str, templates: str = "") -> str:
    """
    Run Nuclei vulnerability scanner against the target.
    
    Args:
        target: Target URL or IP.
        templates: Optional specific templates or tags to use.
    """
    logger.info(f"MCP Tool called: scan_nuclei({target})")
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None, 
            run_nuclei, 
            target, 
            templates,
            False
        )
        if result.get("success"):
            return result.get("stdout", "Success, but no output")
        else:
            return f"Error: {result.get('error')} \n {result.get('stderr')}"
    except Exception as e:
        return f"Tool execution failed: {e}"

@mcp.tool()
async def scan_sqlmap(url: str, batch: bool = True, level: int = 1, risk: int = 1, additional_args: str = "") -> str:
    """
    Run SQLMap to detect and exploit SQL injection flaws.
    
    Args:
        url: Target URL with vulnerable parameter (e.g., http://example.com/vuln.php?id=1).
        batch: Run in non-interactive mode. Default: True.
        level: Level of tests to perform (1-5).
        risk: Risk of tests to perform (1-3).
        additional_args: Any extra sqlmap arguments (e.g., '--dbs').
    """
    logger.info(f"MCP Tool called: scan_sqlmap({url})")
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None, 
            run_sqlmap, 
            url, 
            batch,
            level,
            risk,
            additional_args
        )
        if result.get("success"):
            return result.get("stdout", "Success, but no output")
        else:
            return f"Error: {result.get('error')} \n {result.get('stderr')}"
    except Exception as e:
        return f"Tool execution failed: {e}"

@mcp.tool()
async def scan_hydra(target: str, service: str, username: str = "", user_list: str = "", password: str = "", pass_list: str = "") -> str:
    """
    Run Hydra for online password cracking.
    
    Args:
        target: Target IP or Hostname.
        service: Service name (e.g., 'ssh', 'ftp', 'http-get').
        username: A single username to test.
        user_list: Path to a wordlist of usernames.
        password: A single password to test.
        pass_list: Path to a wordlist of passwords.
    """
    logger.info(f"MCP Tool called: scan_hydra({target}, {service})")
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None, 
            run_hydra, 
            target, 
            service,
            username if username else None,
            user_list if user_list else None,
            password if password else None,
            pass_list if pass_list else None
        )
        if result.get("success"):
            return result.get("stdout", "Success, but no output")
        else:
            return f"Error: {result.get('error')} \n {result.get('stderr')}"
    except Exception as e:
        return f"Tool execution failed: {e}"

@mcp.tool()
async def submit_ai_dag_plan(target: str, task_sequence: str) -> str:
    """
    Submit a custom DAG (Directed Acyclic Graph) of tasks planned by AI for execution.
    This fulfills the 'AI Decomposes Goals into executable task DAGs' requirement.
    
    Args:
        target: Target IP or URL.
        task_sequence: JSON string representing a list of tasks to run sequentially.
                       Format: [{"tool_name": "nmap", "params": {"ports": "80,443"}}, ...]
                       Supported tools: 'nmap', 'gobuster', 'nuclei', 'sqlmap', 'hydra'.
    """
    logger.info(f"MCP Tool called: submit_ai_dag_plan({target})")
    try:
        tasks_data = json.loads(task_sequence)
        job = Job(target=target)
        scheduler.jobs[job.id] = job
        
        # Link tasks sequentially for MVP DAG
        prev_task_id = None
        for t_data in tasks_data:
            tool_name = t_data.get("tool_name")
            params = t_data.get("params", {})
            params["target"] = params.get("target", target) # Auto-inject target if missing
            
            task = Task(tool_name=tool_name, params=params)
            if prev_task_id:
                task.dependencies.append(prev_task_id)
            
            job.tasks.append(task)
            prev_task_id = task.id
            
        scheduler.db.save_job(job)
        
        # Start scheduler asynchronously
        asyncio.create_task(scheduler.run_job(job.id))
        
        return f"AI DAG plan submitted successfully! Job ID: {job.id}. You can check status later via CLI."
    except json.JSONDecodeError:
        return "Error: task_sequence must be a valid JSON array."
    except Exception as e:
        return f"Error scheduling DAG plan: {e}"


def start_server():
    """Start the MCP server on stdio."""
    logger.info("Starting MCP Scan Server")
    mcp.run()

if __name__ == "__main__":
    start_server()
