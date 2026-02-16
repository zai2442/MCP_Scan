import unittest
from command_executor import CommandExecutor

class TestCommandExecutor(unittest.TestCase):
    def test_simple_echo(self):
        executor = CommandExecutor("echo Hello", timeout=5)
        result = executor.execute()
        self.assertIn("Hello", result["stdout"])
        self.assertEqual(result["return_code"], 0)
        self.assertFalse(result["timed_out"])

    def test_timeout(self):
        # Sleep for 3 seconds, but timeout is 1 second
        executor = CommandExecutor("ping -n 3 127.0.0.1", timeout=1) 
        result = executor.execute()
        self.assertTrue(result["timed_out"])
        self.assertNotEqual(result["return_code"], 0)

if __name__ == "__main__":
    unittest.main()
