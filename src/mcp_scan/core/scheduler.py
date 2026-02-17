import asyncio
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime

from mcp_scan.core.models import Job, Task, TaskStatus, Host, Service, Vulnerability
from mcp_scan.core.errors import ToolNotFoundError, SchedulerError
from mcp_scan.tools.nmap_tool import run_nmap
from mcp_scan.tools.nuclei_tool import run_nuclei
from mcp_scan.tools.gobuster_tool import run_gobuster
from mcp_scan.core.db import get_db

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self):
        self.jobs: Dict[UUID, Job] = {}
        self.active_tasks: Dict[UUID, asyncio.Task] = {}
        self.db = get_db()
        # Loop should be retrieved in async context, not init

    async def create_job(self, target: str) -> Job:
        """Initialize a new scan job with default tasks."""
        job = Job(target=target)
        self.jobs[job.id] = job
        
        # Initial Task: Nmap
        # In a real DAG, we'd add this, then subsequent tasks depend on it.
        # For MVP, we'll add Nmap first.
        nmap_task = Task(
            tool_name="nmap",
            params={"target": target, "ports": "top-1000"}
        )
        job.tasks.append(nmap_task)
        
        # Save to DB
        self.db.save_job(job)
        
        return job

    async def run_job(self, job_id: UUID):
        """Main loop to execute tasks for a job."""
        job = self.jobs.get(job_id)
        if not job:
            raise SchedulerError(f"Job {job_id} not found")

        job.status = TaskStatus.RUNNING
        self.db.update_status(job.id, TaskStatus.RUNNING.value)
        logger.info(f"Starting job {job_id} for target {job.target}")

        try:
            # Simple sequential execution for MVP P0 (or simple dependency check)
            # In a full DAG, we'd use a queue and check dependencies.
            # Here, we just iterate through pending tasks, execute them, and add new ones.
            
            # We keep a loop until all tasks are completed
            while True:
                pending_tasks = [t for t in job.tasks if t.status == TaskStatus.PENDING]
                if not pending_tasks:
                    # check if any are running?
                    running = [t for t in job.tasks if t.status == TaskStatus.RUNNING]
                    if not running:
                        break # All done
                    await asyncio.sleep(1) # Wait for running tasks
                    continue

                # Pick a task that is ready (dependencies met)
                # For MVP, we assume order in list is roughly order of execution or independent
                # But let's do a simple check
                ready_tasks = []
                for task in pending_tasks:
                    deps_met = True
                    for dep_id in task.dependencies:
                        dep_task = next((t for t in job.tasks if t.id == dep_id), None)
                        if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                            deps_met = False
                            break
                    if deps_met:
                        ready_tasks.append(task)
                
                if not ready_tasks:
                    # If we have pending tasks but none are ready, and no running tasks -> Deadlock or waiting
                    running = [t for t in job.tasks if t.status == TaskStatus.RUNNING]
                    if not running:
                        logger.error("Deadlock detected or dependencies failed.")
                        job.status = TaskStatus.FAILED
                        self.db.save_job(job) # Save final state
                        return
                    await asyncio.sleep(1)
                    continue

                # Execute ready tasks (concurrency limit could be added here)
                for task in ready_tasks:
                    # Run in background
                    task.status = TaskStatus.RUNNING
                    task.started_at = datetime.now()
                    # Save state before running task
                    self.db.save_job(job)
                    asyncio.create_task(self._execute_task(job, task))
                
                await asyncio.sleep(0.5)

            job.status = TaskStatus.COMPLETED
            self.db.save_job(job) # Save completed state
            logger.info(f"Job {job_id} completed.")

        except Exception as e:
            logger.error(f"Job failed: {e}")
            job.status = TaskStatus.FAILED
            self.db.save_job(job) # Save failed state

    async def _execute_task(self, job: Job, task: Task):
        """Execute a single task and handle results."""
        try:
            logger.info(f"Executing task {task.tool_name} ({task.id})")
            
            # Execute tool wrapper in thread pool
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None, 
                self._run_tool_wrapper, 
                task.tool_name, 
                task.params
            )
            
            task.result = result
            task.completed_at = datetime.now()
            
            if result.get("success", False):
                task.status = TaskStatus.COMPLETED
                self._process_task_result(job, task)
            else:
                task.status = TaskStatus.FAILED
                task.error = result.get("stderr") or result.get("error")
            
            # Save job state after task completion
            self.db.save_job(job)
                
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            self.db.save_job(job)

    def _run_tool_wrapper(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch to the correct tool function."""
        if tool_name == "nmap":
            return run_nmap(**params)
        elif tool_name == "nuclei":
            return run_nuclei(**params)
        elif tool_name == "gobuster":
            # Assuming gobuster tool signature
            return run_gobuster(**params)
        else:
            raise ToolNotFoundError(tool_name)

    def _process_task_result(self, job: Job, task: Task):
        """Analyze result and trigger next steps (DAG Logic)."""
        # This is where the "Intelligent" part happens
        
        if task.tool_name == "nmap":
            # Parse Nmap output (simplistic for MVP)
            # If port 80/443 open, trigger Nuclei and Gobuster
            output = task.result.get("stdout", "")
            
            # Very basic parsing logic
            has_web = "80/tcp" in output or "443/tcp" in output or "http" in output
            
            if has_web:
                logger.info("Web ports detected. Scheduling Nuclei and Gobuster.")
                
                # Create Nuclei Task
                nuclei_task = Task(
                    tool_name="nuclei",
                    params={"target": f"http://{job.target}"}, # Simplified protocol guessing
                    dependencies=[task.id]
                )
                job.tasks.append(nuclei_task)
                
                # Create Gobuster Task
                gobuster_task = Task(
                    tool_name="gobuster",
                    params={"url": f"http://{job.target}"},
                    dependencies=[task.id]
                )
                job.tasks.append(gobuster_task)

    def get_job(self, job_id: UUID) -> Optional[Job]:
        # Try memory first
        if job_id in self.jobs:
            return self.jobs[job_id]
        
        # Try DB
        job = self.db.get_job(job_id)
        if job:
            # Cache back to memory (optional, but good for subsequent access if process is long-running)
            self.jobs[job.id] = job
            return job
            
        return None
