"""
Repository analyzers for different technology stacks
"""
from .detector import detect_tech_stack
from .base import BaseAnalyzer

__all__ = ['detect_tech_stack', 'BaseAnalyzer']
