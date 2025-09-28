"""Fingerprinting utilities for script caching."""

import hashlib
import json
import re
from typing import Any, Dict


def normalize_prompt(prompt: str) -> str:
    """Normalize a prompt for consistent fingerprinting."""
    # Convert to lowercase
    normalized = prompt.lower()
    
    # Remove common stopwords
    stopwords = {
        "please", "can you", "could you", "would you", "i need", "i want",
        "help me", "create", "make", "generate", "build", "write"
    }
    
    for stopword in stopwords:
        normalized = normalized.replace(stopword, "")
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized


def normalize_context(context: Dict[str, Any]) -> str:
    """Normalize context data for consistent fingerprinting."""
    # Sort keys and convert to JSON string
    return json.dumps(context, sort_keys=True, separators=(',', ':'))


def generate_fingerprint(prompt: str, context: Dict[str, Any], language: str = "python", template_version: str = "1.0.0") -> str:
    """Generate a fingerprint for a script request."""
    # Normalize inputs
    norm_prompt = normalize_prompt(prompt)
    norm_context = normalize_context(context)
    
    # Create content string
    content = f"{norm_prompt}|{norm_context}|{language}|{template_version}"
    
    # Generate hash
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def generate_prompt_sha(prompt: str) -> str:
    """Generate SHA hash for normalized prompt."""
    normalized = normalize_prompt(prompt)
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def generate_context_sha(context: Dict[str, Any]) -> str:
    """Generate SHA hash for normalized context."""
    normalized = normalize_context(context)
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]
