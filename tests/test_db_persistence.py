import unittest
import json
from uuid import uuid4
from datetime import datetime
from unittest.mock import MagicMock, patch

from mcp_scan.core.models import Job, TaskStatus
from mcp_scan.core.db import DatabaseManager

class TestDBPersistence(unittest.TestCase):
    def setUp(self):
        # Mock DatabaseManager for unit testing logic
        # For integration testing, we would need a real DB connection
        self.mock_pool = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        
        self.mock_pool.get_connection.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor

    @patch('mcp_scan.core.db.get_config')
    @patch('mysql.connector.pooling.MySQLConnectionPool')
    def test_save_job(self, mock_pool_cls, mock_get_config):
        # Setup mock
        mock_pool_cls.return_value = self.mock_pool
        db = DatabaseManager()
        
        # Create a job
        job = Job(target="127.0.0.1")
        
        # Call save
        db.save_job(job)
        
        # Verify SQL execution
        self.mock_cursor.execute.assert_called()
        call_args = self.mock_cursor.execute.call_args
        # call_args is a tuple: (args, kwargs)
        # args[0] is query, args[1] is params
        query = call_args[0][0]
        params = call_args[0][1]
        
        # Using assertIn because the query might have whitespace/newlines
        self.assertIn("INSERT INTO job_results", query)
        self.assertEqual(params[0], str(job.id))
        self.assertEqual(params[1], "pending")
        
        # Verify JSON serialization
        json_data = params[2]
        parsed = json.loads(json_data)
        self.assertEqual(parsed['target'], "127.0.0.1")
        self.assertEqual(parsed['status'], "pending")

    @patch('mcp_scan.core.db.get_config')
    @patch('mysql.connector.pooling.MySQLConnectionPool')
    def test_get_job(self, mock_pool_cls, mock_get_config):
        # Setup mock
        mock_pool_cls.return_value = self.mock_pool
        db = DatabaseManager()
        
        job_id = uuid4()
        mock_job_data = {
            "id": str(job_id),
            "target": "example.com",
            "status": "completed",
            "tasks": [],
            "assets": [],
            "created_at": datetime.now().isoformat()
        }
        
        # Mock fetch result
        self.mock_cursor.fetchone.return_value = {
            "result_data": json.dumps(mock_job_data)
        }
        
        # Call get
        job = db.get_job(job_id)
        
        # Verify
        self.assertIsNotNone(job)
        self.assertEqual(job.target, "example.com")
        self.assertEqual(job.status, TaskStatus.COMPLETED)
        self.assertEqual(str(job.id), str(job_id))

if __name__ == '__main__':
    unittest.main()
