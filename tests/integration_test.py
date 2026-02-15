import unittest
import asyncio
from unittest.mock import patch, MagicMock
from mcp_scan.core.scheduler import Scheduler
from mcp_scan.core.models import TaskStatus

class IntegrationTest(unittest.TestCase):
    def setUp(self):
        self.scheduler = Scheduler()

    @patch('mcp_scan.core.scheduler.run_gobuster')
    @patch('mcp_scan.core.scheduler.run_nuclei')
    @patch('mcp_scan.core.scheduler.run_nmap')
    def test_full_scan_flow(self, mock_nmap, mock_nuclei, mock_gobuster):
        # Setup mocks with slight delays to simulate real work
        mock_nmap.return_value = {"success": True, "return_code": 0, "stdout": "80/tcp open", "stderr": ""}
        mock_nuclei.return_value = {"success": True, "return_code": 0, "stdout": "Low severity found", "stderr": ""}
        mock_gobuster.return_value = {"success": True, "return_code": 0, "stdout": "/admin found", "stderr": ""}

        async def run():
            # Create 3 concurrent jobs
            jobs = []
            for i in range(3):
                jobs.append(await self.scheduler.create_job(f"192.168.1.{i+1}"))
            
            # Run them concurrently
            tasks = [self.scheduler.run_job(job.id) for job in jobs]
            
            # We expect them to finish reasonably fast with mocks
            await asyncio.gather(*tasks)
            
            # Verify results
            for job in jobs:
                self.assertEqual(job.status, TaskStatus.COMPLETED)
                # Should have 3 tasks: Nmap -> Nuclei, Gobuster
                self.assertEqual(len(job.tasks), 3)
                
        asyncio.run(run())
