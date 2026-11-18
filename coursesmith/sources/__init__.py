"""Source adapters: how a course reads Wikipedia and other vetted sources. See base.py and registry.py."""
from .base import MissingSource, SourceAdapter, SourceError, TIERS, best_tier, tier_rank  # noqa: F401
from .keys import SEP, display, is_qualified, make_key, page_part, split_key  # noqa: F401
from .registry import Registry  # noqa: F401
