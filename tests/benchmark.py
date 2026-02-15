import time
import asyncio
import logging
from unittest.mock import patch
from mcp_scan.core.scheduler import Scheduler

# Disable logging for benchmark
logging.getLogger("mcp_scan").setLevel(logging.CRITICAL)

async def run_benchmark(num_jobs=10):
    scheduler = Scheduler()
    
    # Mock tools to return instantly
    with patch('mcp_scan.core.scheduler.run_nmap') as m1, \
         patch('mcp_scan.core.scheduler.run_nuclei') as m2, \
         patch('mcp_scan.core.scheduler.run_gobuster') as m3:
        
        m1.return_value = {"success": True, "return_code": 0, "stdout": "80/tcp open", "stderr": ""}
        m2.return_value = {"success": True, "return_code": 0, "stdout": "", "stderr": ""}
        m3.return_value = {"success": True, "return_code": 0, "stdout": "", "stderr": ""}
        
        start_time = time.time()
        
        jobs = []
        for i in range(num_jobs):
            jobs.append(await scheduler.create_job(f"10.0.0.{i}"))
            
        tasks = [scheduler.run_job(job.id) for job in jobs]
        await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Benchmark Results:")
        print(f"Total Jobs: {num_jobs}")
        print(f"Total Tasks: {num_jobs * 3}")
        print(f"Duration: {duration:.4f}s")
        print(f"Jobs/sec: {num_jobs/duration:.2f}")

if __name__ == "__main__":
    asyncio.run(run_benchmark(50))
