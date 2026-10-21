from .core import EmailAnalysis, analyze_email, canon_email
from .rules import rules_info, rules_version
from .updater import update_rules

__all__ = [
    "EmailAnalysis",
    "analyze_email",
    "canon_email",
    "rules_info",
    "rules_version",
    "update_rules",
]

__version__ = "0.2.0"
