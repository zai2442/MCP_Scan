import unittest
import asyncio
from unittest.mock import patch, MagicMock
from mcp_scan.core.scheduler import Scheduler
from mcp_scan.core.models import TaskStatus

class IntegrationTest(unittest.TestCase):
    def setUp(self):
        # Patch database to prevent real connection attempts
        self.db_patcher = patch('mcp_scan.core.scheduler.get_db')
        self.mock_get_db = self.db_patcher.start()
        self.mock_db = MagicMock()
        self.mock_get_db.return_value = self.mock_db
        self.addCleanup(self.db_patcher.stop)
        
        self.scheduler = Scheduler()

    @patch('mcp_scan.core.scheduler.run_gobuster')
    @patch('mcp_scan.core.scheduler.run_nuclei')
    @patch('mcp_scan.core.scheduler.run_nmap')
    def test_full_scan_flow(self, mock_nmap, mock_nuclei, mock_gobuster):
        # Setup mocks to return immediately
        mock_nmap.return_value = {"success": True, "return_code": 0, "stdout": "80/tcp open", "stderr": ""}
        mock_nuclei.return_value = {"success": True, "return_code": 0, "stdout": "Low severity found", "stderr": ""}
        mock_gobuster.return_value = {"success": True, "return_code": 0, "stdout": "/admin found", "stderr": ""}

        async def run():
            # Create 3 concurrent jobs
            jobs = []
            for i in range(3):
                jobs.append(await self.scheduler.create_job(f"192.168.1.{i+1}"))
            
            # Run them concurrently with a timeout
            tasks = [self.scheduler.run_job(job.id) for job in jobs]
            
            try:
                # We expect them to finish reasonably fast with mocks
                # Wait for all jobs to complete, but timeout after 2 seconds to avoid hanging
                await asyncio.wait_for(asyncio.gather(*tasks), timeout=2.0)
            except asyncio.TimeoutError:
                # If timeout happens, it means logic is stuck, but we still want to assert state
                pass
            
            # Verify results
            for job in jobs:
                # Check that jobs completed or at least progressed
                # Note: In a real environment, they might be RUNNING if timeout hits, 
                # but with mocks returning immediately, they should be COMPLETED.
                self.assertEqual(job.status, TaskStatus.COMPLETED)
                # Should have 3 tasks: Nmap -> Nuclei, Gobuster
                self.assertEqual(len(job.tasks), 3)
                
        asyncio.run(run())
