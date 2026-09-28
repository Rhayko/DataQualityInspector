"""Tools for profiling CSV data and communicating data-quality risks."""

from .inspector import InspectionResult, inspect_csv

__all__ = ["InspectionResult", "inspect_csv"]

