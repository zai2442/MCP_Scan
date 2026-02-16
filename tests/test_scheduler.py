import unittest
import asyncio
from unittest.mock import MagicMock, patch
from mcp_scan.core.scheduler import Scheduler
from mcp_scan.core.models import TaskStatus

class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.scheduler = Scheduler()

    def test_create_job(self):
        async def run():
            job = await self.scheduler.create_job("127.0.0.1")
            self.assertEqual(job.target, "127.0.0.1")
            self.assertEqual(len(job.tasks), 1)
            self.assertEqual(job.tasks[0].tool_name, "nmap")
        asyncio.run(run())

    @patch('mcp_scan.core.scheduler.run_nmap')
    def test_run_job_flow(self, mock_nmap):
        # Mock Nmap result to trigger next steps
        mock_nmap.return_value = {
            "success": True, 
            "return_code": 0, 
            "stdout": "80/tcp open http", 
            "stderr": ""
        }

        async def run():
            job = await self.scheduler.create_job("example.com")
            
            # Use a timeout to prevent infinite loop if logic fails
            try:
                await asyncio.wait_for(self.scheduler.run_job(job.id), timeout=2.0)
            except asyncio.TimeoutError:
                pass # Expected if we don't mock nuclei/gobuster, but let's see

            # Check if Nmap finished
            self.assertEqual(job.tasks[0].status, TaskStatus.COMPLETED)
            
            # Check if Nuclei/Gobuster were added
            self.assertTrue(any(t.tool_name == "nuclei" for t in job.tasks))
            self.assertTrue(any(t.tool_name == "gobuster" for t in job.tasks))
        
        asyncio.run(run())
