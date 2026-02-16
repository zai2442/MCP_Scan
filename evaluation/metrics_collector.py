"""
Metrics Collector for Comparative Experiments

This module collects and analyzes metrics for comparing serial vs collaborative
penetration testing approaches.
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import statistics
import logging

logger = logging.getLogger(__name__)


@dataclass
class TaskMetrics:
    """Individual task execution metrics"""
    task_id: str
    task_type: str  # 'port_scan', 'web_discovery', 'vuln_verify'
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None  # in seconds
    status: str = 'pending'  # 'pending', 'running', 'completed', 'failed'
    node_id: str = ''
    vulnerabilities_found: int = 0
    assets_discovered: int = 0
    error_count: int = 0
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None


@dataclass
class ExperimentMetrics:
    """Overall experiment metrics"""
    experiment_id: str
    approach: str  # 'serial', 'collaborative'
    target_scope: str  # e.g., '192.168.1.0/24'
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration: Optional[float] = None
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_vulnerabilities: int = 0
    total_assets: int = 0
    nodes_used: int = 1
    avg_task_duration: Optional[float] = None
    peak_memory_usage: Optional[float] = None
    peak_cpu_usage: Optional[float] = None


class MetricsCollector:
    """Collects and manages metrics for penetration testing experiments"""
    
    def __init__(self, experiment_id: str, approach: str):
        self.experiment_id = experiment_id
        self.approach = approach
        self.tasks: Dict[str, TaskMetrics] = {}
        self.experiment_metrics = ExperimentMetrics(
            experiment_id=experiment_id,
            approach=approach,
            target_scope="",
            start_time=datetime.now()
        )
        self._lock = threading.Lock()
        self._monitoring_active = False
        self._monitor_thread = None
        
    def start_task(self, task_id: str, task_type: str, node_id: str = '') -> None:
        """Start tracking a new task"""
        with self._lock:
            if task_id in self.tasks:
                logger.warning(f"Task {task_id} already exists")
                return
                
            task = TaskMetrics(
                task_id=task_id,
                task_type=task_type,
                start_time=datetime.now(),
                node_id=node_id,
                status='running'
            )
            self.tasks[task_id] = task
            self.experiment_metrics.total_tasks += 1
            
        logger.info(f"Started tracking task {task_id} of type {task_type}")
    
    def complete_task(self, task_id: str, vulnerabilities_found: int = 0, 
                     assets_discovered: int = 0, error_count: int = 0) -> None:
        """Mark a task as completed and record results"""
        with self._lock:
            if task_id not in self.tasks:
                logger.error(f"Task {task_id} not found")
                return
                
            task = self.tasks[task_id]
            task.end_time = datetime.now()
            task.duration = (task.end_time - task.start_time).total_seconds()
            task.status = 'completed'
            task.vulnerabilities_found = vulnerabilities_found
            task.assets_discovered = assets_discovered
            task.error_count = error_count
            
            self.experiment_metrics.completed_tasks += 1
            self.experiment_metrics.total_vulnerabilities += vulnerabilities_found
            self.experiment_metrics.total_assets += assets_discovered
            
        logger.info(f"Completed task {task_id} in {task.duration:.2f}s")
    
    def fail_task(self, task_id: str, error_count: int = 1) -> None:
        """Mark a task as failed"""
        with self._lock:
            if task_id not in self.tasks:
                logger.error(f"Task {task_id} not found")
                return
                
            task = self.tasks[task_id]
            task.end_time = datetime.now()
            task.duration = (task.end_time - task.start_time).total_seconds()
            task.status = 'failed'
            task.error_count = error_count
            
            self.experiment_metrics.failed_tasks += 1
            
        logger.error(f"Task {task_id} failed after {task.duration:.2f}s")
    
    def set_target_scope(self, scope: str) -> None:
        """Set the target scope for the experiment"""
        with self._lock:
            self.experiment_metrics.target_scope = scope
    
    def set_nodes_used(self, count: int) -> None:
        """Set the number of nodes used in the experiment"""
        with self._lock:
            self.experiment_metrics.nodes_used = count
    
    def start_monitoring(self, interval: float = 1.0) -> None:
        """Start system resource monitoring"""
        if self._monitoring_active:
            return
            
        self._monitoring_active = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_resources, 
            args=(interval,),
            daemon=True
        )
        self._monitor_thread.start()
        logger.info("Started resource monitoring")
    
    def stop_monitoring(self) -> None:
        """Stop system resource monitoring"""
        self._monitoring_active = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        logger.info("Stopped resource monitoring")
    
    def _monitor_resources(self, interval: float) -> None:
        """Monitor system resources in background"""
        try:
            import psutil
        except ImportError:
            logger.warning("psutil not available, resource monitoring disabled")
            return
            
        while self._monitoring_active:
            try:
                cpu_percent = psutil.cpu_percent(interval=None)
                memory_percent = psutil.virtual_memory().percent
                
                with self._lock:
                    # Update peak values
                    if (self.experiment_metrics.peak_cpu_usage is None or 
                        cpu_percent > self.experiment_metrics.peak_cpu_usage):
                        self.experiment_metrics.peak_cpu_usage = cpu_percent
                        
                    if (self.experiment_metrics.peak_memory_usage is None or 
                        memory_percent > self.experiment_metrics.peak_memory_usage):
                        self.experiment_metrics.peak_memory_usage = memory_percent
                
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                break
    
    def finalize_experiment(self) -> ExperimentMetrics:
        """Finalize the experiment and calculate final metrics"""
        with self._lock:
            self.experiment_metrics.end_time = datetime.now()
            self.experiment_metrics.total_duration = (
                self.experiment_metrics.end_time - 
                self.experiment_metrics.start_time
            ).total_seconds()
            
            # Calculate average task duration
            completed_tasks = [
                task for task in self.tasks.values() 
                if task.status == 'completed' and task.duration is not None
            ]
            
            if completed_tasks:
                self.experiment_metrics.avg_task_duration = statistics.mean(
                    [task.duration for task in completed_tasks]
                )
            
            self.stop_monitoring()
            
        logger.info(f"Experiment {self.experiment_id} finalized")
        return self.experiment_metrics
    
    def get_task_metrics(self, task_id: str) -> Optional[TaskMetrics]:
        """Get metrics for a specific task"""
        with self._lock:
            return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[TaskMetrics]:
        """Get all task metrics"""
        with self._lock:
            return list(self.tasks.values())
    
    def get_tasks_by_type(self, task_type: str) -> List[TaskMetrics]:
        """Get tasks filtered by type"""
        with self._lock:
            return [task for task in self.tasks.values() if task.task_type == task_type]
    
    def get_experiment_summary(self) -> Dict[str, Any]:
        """Get a summary of experiment metrics"""
        with self._lock:
            summary = asdict(self.experiment_metrics)
            
            # Add additional calculated metrics
            if self.experiment_metrics.total_tasks > 0:
                summary['success_rate'] = (
                    self.experiment_metrics.completed_tasks / 
                    self.experiment_metrics.total_tasks
                )
                summary['failure_rate'] = (
                    self.experiment_metrics.failed_tasks / 
                    self.experiment_metrics.total_tasks
                )
            else:
                summary['success_rate'] = 0.0
                summary['failure_rate'] = 0.0
            
            if self.experiment_metrics.total_duration > 0:
                summary['tasks_per_second'] = (
                    self.experiment_metrics.completed_tasks / 
                    self.experiment_metrics.total_duration
                )
                summary['vulnerabilities_per_hour'] = (
                    self.experiment_metrics.total_vulnerabilities * 3600 / 
                    self.experiment_metrics.total_duration
                )
            else:
                summary['tasks_per_second'] = 0.0
                summary['vulnerabilities_per_hour'] = 0.0
            
            return summary
    
    def save_metrics(self, filepath: str) -> None:
        """Save metrics to JSON file"""
        try:
            data = {
                'experiment': asdict(self.experiment_metrics),
                'tasks': [asdict(task) for task in self.tasks.values()],
                'summary': self.get_experiment_summary()
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
            logger.info(f"Metrics saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def load_metrics(self, filepath: str) -> None:
        """Load metrics from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Load experiment metrics
            exp_data = data['experiment']
            self.experiment_metrics = ExperimentMetrics(**exp_data)
            
            # Load task metrics
            self.tasks.clear()
            for task_data in data['tasks']:
                # Convert string timestamps back to datetime objects
                task_data['start_time'] = datetime.fromisoformat(task_data['start_time'])
                if task_data['end_time']:
                    task_data['end_time'] = datetime.fromisoformat(task_data['end_time'])
                
                task = TaskMetrics(**task_data)
                self.tasks[task.task_id] = task
            
            logger.info(f"Metrics loaded from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")
    
    def compare_with(self, other: 'MetricsCollector') -> Dict[str, Any]:
        """Compare this experiment with another"""
        my_summary = self.get_experiment_summary()
        other_summary = other.get_experiment_summary()
        
        comparison = {
            'experiment_1': {
                'id': self.experiment_id,
                'approach': self.approach,
                **my_summary
            },
            'experiment_2': {
                'id': other.experiment_id,
                'approach': other.approach,
                **other_summary
            },
            'comparison': {
                'duration_improvement': (
                    (other_summary['total_duration'] - my_summary['total_duration']) /
                    other_summary['total_duration'] * 100
                ) if other_summary['total_duration'] > 0 else 0,
                'vulnerability_improvement': (
                    my_summary['total_vulnerabilities'] - 
                    other_summary['total_vulnerabilities']
                ),
                'efficiency_improvement': (
                    (my_summary['vulnerabilities_per_hour'] - 
                     other_summary['vulnerabilities_per_hour']) /
                    other_summary['vulnerabilities_per_hour'] * 100
                ) if other_summary['vulnerabilities_per_hour'] > 0 else 0,
                'success_rate_improvement': (
                    (my_summary['success_rate'] - other_summary['success_rate']) * 100
                )
            }
        }
        
        return comparison


# Example usage and utility functions
def create_experiment_comparison(serial_metrics: MetricsCollector, 
                               collaborative_metrics: MetricsCollector) -> str:
    """Create a formatted comparison report"""
    comparison = serial_metrics.compare_with(collaborative_metrics)
    
    report = f"""
# Experiment Comparison Report

## Serial Approach ({comparison['experiment_1']['id']})
- Total Duration: {comparison['experiment_1']['total_duration']:.2f}s
- Vulnerabilities Found: {comparison['experiment_1']['total_vulnerabilities']}
- Success Rate: {comparison['experiment_1']['success_rate']:.2%}
- Tasks/Second: {comparison['experiment_1']['tasks_per_second']:.2f}

## Collaborative Approach ({comparison['experiment_2']['id']})
- Total Duration: {comparison['experiment_2']['total_duration']:.2f}s
- Vulnerabilities Found: {comparison['experiment_2']['total_vulnerabilities']}
- Success Rate: {comparison['experiment_2']['success_rate']:.2%}
- Tasks/Second: {comparison['experiment_2']['tasks_per_second']:.2f}

## Performance Improvements
- Duration Improvement: {comparison['comparison']['duration_improvement']:.1f}%
- Additional Vulnerabilities: {comparison['comparison']['vulnerability_improvement']}
- Efficiency Improvement: {comparison['comparison']['efficiency_improvement']:.1f}%
- Success Rate Improvement: {comparison['comparison']['success_rate_improvement']:.1f}%
"""
    
    return report
