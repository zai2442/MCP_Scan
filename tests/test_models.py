import unittest
from mcp_scan.core.models import Job, Task, TaskStatus, Host

class TestModels(unittest.TestCase):
    def test_job_creation(self):
        job = Job(target="127.0.0.1")
        self.assertEqual(job.target, "127.0.0.1")
        self.assertEqual(job.status, TaskStatus.PENDING)
        self.assertIsNotNone(job.id)

    def test_task_status(self):
        task = Task(tool_name="nmap")
        self.assertEqual(task.status, TaskStatus.PENDING)
        task.status = TaskStatus.RUNNING
        self.assertEqual(task.status, "running")

    def test_host_model(self):
        host = Host(ip="192.168.1.1")
        self.assertEqual(host.ip, "192.168.1.1")
