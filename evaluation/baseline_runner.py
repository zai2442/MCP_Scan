"""
Baseline Runner for Traditional Serial Penetration Testing

This module implements traditional serial penetration testing workflows
to serve as a baseline for comparison with collaborative approaches.
"""

import subprocess
import time
import json
import logging
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import tempfile
import os

from .metrics_collector import MetricsCollector

logger = logging.getLogger(__name__)


@dataclass
class BaselineConfig:
    """Configuration for baseline serial testing"""
    target: str  # IP range or hostname
    scan_types: List[str]  # ['port_scan', 'web_discovery', 'vuln_scan']
    tools: Dict[str, str]  # Tool paths
    output_dir: str  # Output directory for results
    timeout: int = 3600  # Global timeout in seconds
    parallel_tasks: int = 1  # Always 1 for serial execution


@dataclass
class ScanResult:
    """Result of a single scan operation"""
    scan_type: str
    target: str
    start_time: datetime
    end_time: datetime
    duration: float
    success: bool
    output_file: str
    vulnerabilities_found: int = 0
    assets_discovered: int = 0
    error_message: str = ""


class BaselineRunner:
    """Traditional serial penetration testing runner"""
    
    def __init__(self, config: BaselineConfig, metrics_collector: MetricsCollector):
        self.config = config
        self.metrics = metrics_collector
        self.results: List[ScanResult] = []
        self.current_task_id: Optional[str] = None
        
        # Ensure output directory exists
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Default tool configurations
        self.default_tools = {
            'nmap': '/usr/bin/nmap',
            'gobuster': '/usr/bin/gobuster',
            'nuclei': '/usr/bin/nuclei',
            'nikto': '/usr/bin/nikto'
        }
        
        # Merge with provided tools
        self.tools = {**self.default_tools, **config.tools}
        
    def run_baseline_test(self) -> List[ScanResult]:
        """Execute the complete baseline serial test"""
        logger.info(f"Starting baseline serial test for {self.config.target}")
        
        self.results.clear()
        start_time = datetime.now()
        
        try:
            # Execute scans in serial order
            for scan_type in self.config.scan_types:
                result = self._run_single_scan(scan_type)
                if result:
                    self.results.append(result)
                else:
                    logger.error(f"Failed to execute {scan_type} scan")
        
        except Exception as e:
            logger.error(f"Baseline test failed: {e}")
        
        total_duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Baseline test completed in {total_duration:.2f} seconds")
        
        return self.results
    
    def _run_single_scan(self, scan_type: str) -> Optional[ScanResult]:
        """Execute a single scan operation"""
        task_id = f"{scan_type}_{int(time.time())}"
        self.current_task_id = task_id
        
        # Start metrics tracking
        self.metrics.start_task(task_id, scan_type, node_id="baseline_serial")
        
        start_time = datetime.now()
        
        try:
            if scan_type == 'port_scan':
                result = self._run_port_scan()
            elif scan_type == 'web_discovery':
                result = self._run_web_discovery()
            elif scan_type == 'vuln_scan':
                result = self._run_vulnerability_scan()
            elif scan_type == 'subdomain_enum':
                result = self._run_subdomain_enumeration()
            elif scan_type == 'smb_enum':
                result = self._run_smb_enumeration()
            else:
                raise ValueError(f"Unsupported scan type: {scan_type}")
            
            # Update metrics with results
            self.metrics.complete_task(
                task_id, 
                vulnerabilities_found=result.vulnerabilities_found,
                assets_discovered=result.assets_discovered
            )
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Scan {scan_type} failed: {error_msg}")
            
            # Record failure in metrics
            self.metrics.fail_task(task_id, error_count=1)
            
            # Create failed result
            return ScanResult(
                scan_type=scan_type,
                target=self.config.target,
                start_time=start_time,
                end_time=datetime.now(),
                duration=(datetime.now() - start_time).total_seconds(),
                success=False,
                output_file="",
                error_message=error_msg
            )
    
    def _run_port_scan(self) -> ScanResult:
        """Execute Nmap port scan"""
        start_time = datetime.now()
        output_file = os.path.join(self.config.output_dir, "nmap_results.xml")
        
        cmd = [
            self.tools['nmap'],
            '-sS',  # SYN scan
            '-p', '1-1000',  # Port range
            '-T3',  # Timing template
            '-oX', output_file,  # XML output
            '-oA', os.path.join(self.config.output_dir, "nmap_results"),  # All formats
            self.config.target
        ]
        
        logger.info(f"Running port scan: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if result.returncode != 0:
                raise Exception(f"Nmap failed: {result.stderr}")
            
            # Parse results
            vulnerabilities_found, assets_discovered = self._parse_nmap_results(output_file)
            
            return ScanResult(
                scan_type='port_scan',
                target=self.config.target,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                success=True,
                output_file=output_file,
                vulnerabilities_found=vulnerabilities_found,
                assets_discovered=assets_discovered
            )
            
        except subprocess.TimeoutExpired:
            raise Exception("Port scan timed out")
        except Exception as e:
            raise Exception(f"Port scan execution failed: {e}")
    
    def _run_web_discovery(self) -> ScanResult:
        """Execute Gobuster web discovery"""
        start_time = datetime.now()
        output_file = os.path.join(self.config.output_dir, "gobuster_results.txt")
        
        # Find open web ports from previous nmap scan
        web_ports = self._get_web_ports()
        
        if not web_ports:
            # Default to common web ports
            web_ports = [80, 443, 8080, 8443]
        
        all_vulnerabilities = 0
        all_assets = 0
        
        for port in web_ports:
            target_url = f"http://{self.config.target}:{port}"
            port_output_file = f"{output_file}.port{port}"
            
            cmd = [
                self.tools['gobuster'],
                'dir',
                '-u', target_url,
                '-w', '/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt',
                '-o', port_output_file,
                '-t', '10',  # 10 threads
                '-q'  # Quiet mode
            ]
            
            logger.info(f"Running web discovery on port {port}: {' '.join(cmd)}")
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes per port
                )
                
                if result.returncode == 0:
                    vulns, assets = self._parse_gobuster_results(port_output_file)
                    all_vulnerabilities += vulns
                    all_assets += assets
                else:
                    logger.warning(f"Gobuster failed on port {port}: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                logger.warning(f"Gobuster timed out on port {port}")
            except Exception as e:
                logger.warning(f"Gobuster error on port {port}: {e}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return ScanResult(
            scan_type='web_discovery',
            target=self.config.target,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            success=True,
            output_file=output_file,
            vulnerabilities_found=all_vulnerabilities,
            assets_discovered=all_assets
        )
    
    def _run_vulnerability_scan(self) -> ScanResult:
        """Execute Nuclei vulnerability scan"""
        start_time = datetime.now()
        output_file = os.path.join(self.config.output_dir, "nuclei_results.json")
        
        cmd = [
            self.tools['nuclei'],
            '-target', self.config.target,
            '-json',  # JSON output
            '-o', output_file,
            '-t', '/usr/share/nuclei/templates/',  # Use default templates
            '-severity', 'medium,high,critical',  # Focus on important vulns
            '-silent'  # Reduce noise
        ]
        
        logger.info(f"Running vulnerability scan: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if result.returncode != 0 and result.returncode != 1:  # 1 means no vulns found
                raise Exception(f"Nuclei failed: {result.stderr}")
            
            # Parse results
            vulnerabilities_found, assets_discovered = self._parse_nuclei_results(output_file)
            
            return ScanResult(
                scan_type='vuln_scan',
                target=self.config.target,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                success=True,
                output_file=output_file,
                vulnerabilities_found=vulnerabilities_found,
                assets_discovered=assets_discovered
            )
            
        except subprocess.TimeoutExpired:
            raise Exception("Vulnerability scan timed out")
        except Exception as e:
            raise Exception(f"Vulnerability scan execution failed: {e}")
    
    def _run_subdomain_enumeration(self) -> ScanResult:
        """Execute subdomain enumeration (placeholder)"""
        start_time = datetime.now()
        
        # Placeholder implementation - would typically use tools like amass, subfinder
        logger.info("Subdomain enumeration not implemented in baseline")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return ScanResult(
            scan_type='subdomain_enum',
            target=self.config.target,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            success=True,
            output_file="",
            vulnerabilities_found=0,
            assets_discovered=0
        )
    
    def _run_smb_enumeration(self) -> ScanResult:
        """Execute SMB enumeration (placeholder)"""
        start_time = datetime.now()
        
        # Placeholder implementation - would typically use tools like smbmap, enum4linux
        logger.info("SMB enumeration not implemented in baseline")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return ScanResult(
            scan_type='smb_enum',
            target=self.config.target,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            success=True,
            output_file="",
            vulnerabilities_found=0,
            assets_discovered=0
        )
    
    def _get_web_ports(self) -> List[int]:
        """Extract web ports from previous nmap results"""
        nmap_file = os.path.join(self.config.output_dir, "nmap_results.xml")
        
        if not os.path.exists(nmap_file):
            return []
        
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(nmap_file)
            root = tree.getroot()
            
            web_ports = []
            for port in root.findall('.//port'):
                if port.get('protocol') == 'tcp':
                    service = port.find('service')
                    if service is not None:
                        name = service.get('name', '').lower()
                        if any(web_service in name for web_service in ['http', 'ssl', 'https']):
                            port_id = port.get('portid')
                            if port_id:
                                web_ports.append(int(port_id))
            
            return web_ports
            
        except Exception as e:
            logger.warning(f"Failed to parse nmap results: {e}")
            return []
    
    def _parse_nmap_results(self, output_file: str) -> tuple[int, int]:
        """Parse nmap XML results to extract vulnerabilities and assets"""
        if not os.path.exists(output_file):
            return 0, 0
        
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(output_file)
            root = tree.getroot()
            
            assets_discovered = 0
            vulnerabilities_found = 0
            
            # Count hosts and services as assets
            for host in root.findall('.//host'):
                if host.find('.//status').get('state') == 'up':
                    assets_discovered += 1
                    
                    # Count open ports as additional assets
                    for port in host.findall('.//port'):
                        if port.find('.//state').get('state') == 'open':
                            assets_discovered += 1
                            
                            # Simple vulnerability detection based on service
                            service = port.find('.//service')
                            if service is not None:
                                name = service.get('name', '').lower()
                                version = service.get('version', '').lower()
                                
                                # Check for vulnerable services
                                if any(vuln in name for vuln in ['telnet', 'ftp', 'rsh']):
                                    vulnerabilities_found += 1
                                if any(vuln in version for vuln in ['2.3.4', '1.0', 'beta']):
                                    vulnerabilities_found += 1
            
            return vulnerabilities_found, assets_discovered
            
        except Exception as e:
            logger.warning(f"Failed to parse nmap results: {e}")
            return 0, 0
    
    def _parse_gobuster_results(self, output_file: str) -> tuple[int, int]:
        """Parse gobuster results to extract findings"""
        if not os.path.exists(output_file):
            return 0, 0
        
        try:
            assets_discovered = 0
            vulnerabilities_found = 0
            
            with open(output_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('='):
                        assets_discovered += 1
                        
                        # Simple vulnerability detection
                        if any(vuln in line.lower() for vuln in ['admin', 'backup', 'config', 'test']):
                            vulnerabilities_found += 1
            
            return vulnerabilities_found, assets_discovered
            
        except Exception as e:
            logger.warning(f"Failed to parse gobuster results: {e}")
            return 0, 0
    
    def _parse_nuclei_results(self, output_file: str) -> tuple[int, int]:
        """Parse nuclei JSON results"""
        if not os.path.exists(output_file):
            return 0, 0
        
        try:
            vulnerabilities_found = 0
            assets_discovered = 0
            
            with open(output_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            result = json.loads(line)
                            if result.get('template-id'):
                                vulnerabilities_found += 1
                                assets_discovered += 1
                        except json.JSONDecodeError:
                            continue
            
            return vulnerabilities_found, assets_discovered
            
        except Exception as e:
            logger.warning(f"Failed to parse nuclei results: {e}")
            return 0, 0
    
    def save_results(self, filepath: str) -> None:
        """Save baseline results to JSON file"""
        try:
            data = {
                'config': asdict(self.config),
                'results': [asdict(result) for result in self.results],
                'summary': {
                    'total_scans': len(self.results),
                    'successful_scans': sum(1 for r in self.results if r.success),
                    'total_duration': sum(r.duration for r in self.results),
                    'total_vulnerabilities': sum(r.vulnerabilities_found for r in self.results),
                    'total_assets': sum(r.assets_discovered for r in self.results)
                }
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
            logger.info(f"Baseline results saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save baseline results: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of baseline execution"""
        if not self.results:
            return {}
        
        return {
            'total_scans': len(self.results),
            'successful_scans': sum(1 for r in self.results if r.success),
            'total_duration': sum(r.duration for r in self.results),
            'total_vulnerabilities': sum(r.vulnerabilities_found for r in self.results),
            'total_assets': sum(r.assets_discovered for r in self.results),
            'average_scan_duration': sum(r.duration for r in self.results) / len(self.results),
            'scan_types': [r.scan_type for r in self.results],
            'success_rate': sum(1 for r in self.results if r.success) / len(self.results)
        }


# Utility functions for creating and running baseline tests
def create_baseline_config(target: str, output_dir: str) -> BaselineConfig:
    """Create a default baseline configuration"""
    return BaselineConfig(
        target=target,
        scan_types=['port_scan', 'web_discovery', 'vuln_scan'],
        tools={},
        output_dir=output_dir,
        timeout=3600
    )


def run_baseline_experiment(target: str, output_dir: str) -> tuple[List[ScanResult], MetricsCollector]:
    """Run a complete baseline experiment"""
    config = create_baseline_config(target, output_dir)
    
    # Create metrics collector for baseline
    experiment_id = f"baseline_{target.replace('.', '_')}_{int(time.time())}"
    metrics = MetricsCollector(experiment_id, "serial")
    metrics.set_target_scope(target)
    metrics.set_nodes_used(1)
    metrics.start_monitoring()
    
    # Run baseline test
    runner = BaselineRunner(config, metrics)
    results = runner.run_baseline_test()
    
    # Finalize metrics
    metrics.finalize_experiment()
    
    # Save results
    runner.save_results(os.path.join(output_dir, "baseline_results.json"))
    metrics.save_metrics(os.path.join(output_dir, "baseline_metrics.json"))
    
    return results, metrics
