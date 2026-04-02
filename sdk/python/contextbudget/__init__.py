"""ContextBudget SDK -- automatic AI context token tracking.

Usage:
    from contextbudget import track
    from anthropic import Anthropic

    client = track(Anthropic())
    # Every API call now auto-reports token usage to your dashboard
"""

from .wrapper import track

__version__ = "0.1.0"
__all__ = ["track"]
