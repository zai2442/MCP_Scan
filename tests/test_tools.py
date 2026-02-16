import unittest
from unittest.mock import patch, MagicMock
from mcp_scan.tools.nmap_tool import run_nmap
from mcp_scan.tools.nuclei_tool import run_nuclei
from mcp_scan.tools.gobuster_tool import run_gobuster
from mcp_scan.tools.sqlmap_tool import run_sqlmap
from mcp_scan.tools.metasploit_tool import run_metasploit
from mcp_scan.tools.hydra_tool import run_hydra

class TestTools(unittest.TestCase):
    
    @patch('mcp_scan.tools.nmap_tool.CommandExecutor')
    def test_nmap_command_generation(self, MockExecutor):
        # Setup mock
        mock_instance = MockExecutor.return_value
        mock_instance.execute.return_value = {
            "stdout": "Starting Nmap...", 
            "stderr": "", 
            "return_code": 0, 
            "timed_out": False
        }
        
        # Test default
        run_nmap("127.0.0.1")
        
        # Verify command construction
        MockExecutor.assert_called_with("nmap -T3 --top-ports 1000 127.0.0.1", timeout=300)
        
        # Test with options
        run_nmap("example.com", ports="80,443", timing="T4")
        MockExecutor.assert_called_with("nmap -T4 -p 80,443 example.com", timeout=300)

    @patch('mcp_scan.tools.nuclei_tool.CommandExecutor')
    def test_nuclei_command_generation(self, MockExecutor):
        mock_instance = MockExecutor.return_value
        mock_instance.execute.return_value = {"return_code": 0}
        
        run_nuclei("http://example.com", tags=["cve", "misc"])
        
        MockExecutor.assert_called_with("nuclei -target http://example.com -tags cve,misc -rate-limit 50", timeout=600)

    @patch('mcp_scan.tools.gobuster_tool.CommandExecutor')
    def test_gobuster_command_generation(self, MockExecutor):
        mock_instance = MockExecutor.return_value
        mock_instance.execute.return_value = {"return_code": 0}
        
        run_gobuster("http://example.com", wordlist="wordlist.txt", threads=20)
        
        MockExecutor.assert_called_with("gobuster dir -u http://example.com -w wordlist.txt -t 20", timeout=600)

    @patch('mcp_scan.tools.sqlmap_tool.CommandExecutor')
    def test_sqlmap_command_generation(self, MockExecutor):
        mock_instance = MockExecutor.return_value
        mock_instance.execute.return_value = {"return_code": 0}
        
        run_sqlmap("http://example.com", level=3, risk=1)
        
        MockExecutor.assert_called_with("sqlmap -u http://example.com --batch --level=3 --risk=1", timeout=600)

    @patch('mcp_scan.tools.metasploit_tool.CommandExecutor')
    @patch('mcp_scan.tools.metasploit_tool.tempfile.mkstemp')
    @patch('mcp_scan.tools.metasploit_tool.os.fdopen')
    @patch('mcp_scan.tools.metasploit_tool.os.remove')
    def test_metasploit_command(self, mock_remove, mock_fdopen, mock_mkstemp, MockExecutor):
        mock_mkstemp.return_value = (123, "/tmp/test.rc")
        mock_file = MagicMock()
        mock_fdopen.return_value.__enter__.return_value = mock_file
        
        MockExecutor.return_value.execute.return_value = {"return_code": 0}
        
        run_metasploit("exploit/windows/smb/ms17_010_eternalblue", {"RHOSTS": "10.0.0.1"})
        
        MockExecutor.assert_called_with("msfconsole -q -r /tmp/test.rc", timeout=600)
        # Verify file content logic (simple check)
        # The calls are multiple writes, we can check if they happened
        self.assertTrue(mock_file.write.called)

    @patch('mcp_scan.tools.hydra_tool.CommandExecutor')
    def test_hydra_command(self, MockExecutor):
        MockExecutor.return_value.execute.return_value = {"return_code": 0}
        
        run_hydra("10.0.0.1", "ssh", username="admin", password="password")
        
        MockExecutor.assert_called_with("hydra -t 4 -l admin -p password 10.0.0.1 ssh", timeout=600)

if __name__ == '__main__':
    unittest.main()
