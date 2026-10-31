"""
GitHub Morph - A smart tool for treating GitHub as a library of parts.
"""

from .github_morph import GitHubMorph, GitHubRepo, CodeComponent, PatternMatch
from .morph_advanced import AdvancedGitHubMorph, CodePattern, ComponentLibrary

__version__ = "1.0.0"
__all__ = [
    "GitHubMorph",
    "GitHubRepo", 
    "CodeComponent",
    "PatternMatch",
    "AdvancedGitHubMorph",
    "CodePattern",
    "ComponentLibrary"
]