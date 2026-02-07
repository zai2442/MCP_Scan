import subprocess
import threading
import logging
import sys
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

COMMAND_TIMEOUT = 180  # 5 minutes default timeout

class CommandExecutor:
    """Class to handle command execution with better timeout management"""
    
    def __init__(self, command: str, timeout: int = COMMAND_TIMEOUT):
        self.command = command
        self.timeout = timeout
        self.process = None
        self.stdout_data = ""
        self.stderr_data = ""
        self.stdout_thread = None
        self.stderr_thread = None
        self.return_code = None
        self.timed_out = False
    
    def _read_stdout(self):
        """Thread function to continuously read stdout"""
        if self.process and self.process.stdout:
            for line in iter(self.process.stdout.readline, ''):
                self.stdout_data += line
    
    def _read_stderr(self):
        """Thread function to continuously read stderr"""
        if self.process and self.process.stderr:
            for line in iter(self.process.stderr.readline, ''):
                self.stderr_data += line
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command and handle timeout gracefully"""
        logger.info(f"Executing command: {self.command}")
        
        try:
            self.process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            
            # Start threads to read output continuously
            self.stdout_thread = threading.Thread(target=self._read_stdout)
            self.stderr_thread = threading.Thread(target=self._read_stderr)
            self.stdout_thread.daemon = True
            self.stderr_thread.daemon = True
            self.stdout_thread.start()
            self.stderr_thread.start()
            
            # Wait for the process to complete or timeout
            try:
                self.return_code = self.process.wait(timeout=self.timeout)
                # Process completed, join the threads
                self.stdout_thread.join()
                self.stderr_thread.join()
            except subprocess.TimeoutExpired:
                # Process timed out but we might have partial results
                self.timed_out = True
                logger.warning(f"Command timed out after {self.timeout} seconds. Terminating process.")
                
                # Try to terminate gracefully first
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)  # Give it 5 seconds to terminate
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't terminate
                    logger.warning("Process not responding to termination. Killing.")
                    self.process.kill()
                
                self.stdout_thread.join(timeout=1.0)
                self.stderr_thread.join(timeout=1.0)
                self.return_code = -1

            return {
                "command": self.command,
                "stdout": self.stdout_data,
                "stderr": self.stderr_data,
                "return_code": self.return_code,
                "timed_out": self.timed_out
            }

        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return {
                "command": self.command,
                "stdout": self.stdout_data,
                "stderr": str(e),
                "return_code": -1,
                "timed_out": False
            }
