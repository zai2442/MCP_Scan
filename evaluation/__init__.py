"""
Evaluation module for comparative experiments and quantitative evaluation.
"""

from .metrics_collector import MetricsCollector
from .baseline_runner import BaselineRunner

__all__ = ['MetricsCollector', 'BaselineRunner']
