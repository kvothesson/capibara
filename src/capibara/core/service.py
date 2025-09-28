"""Capibara Core service implementation."""

import hashlib
import json
import os
from datetime import datetime
from typing import Dict, Any

from .models import GenerationRequest, GenerationResponse, ScriptManifest, UpdateRequest, UpdateResponse
from .llm_service import GroqLLMService


class CapibaraCore:
    """Capibara Core service for script generation."""
    
    def __init__(self, use_groq: bool = True):
        """Initialize Capibara Core service."""
        self.template_version = "1.0.0"
        
        # Use Groq LLM service
        if not os.environ.get("GROQ_API_KEY"):
            raise ValueError("GROQ_API_KEY environment variable is required. Please set your Groq API key.")
        
        try:
            self.llm = GroqLLMService()
        except Exception as e:
            raise Exception(f"Failed to initialize Groq LLM: {e}")
    
    def generate_script(self, request: GenerationRequest) -> GenerationResponse:
        """Generate a script from a prompt and context."""
        try:
            # Generate script using Groq LLM
            result = self.llm.generate_script(request.prompt, request.context)
            
            # Generate fingerprint
            fingerprint = self._generate_fingerprint(request)
            
            # Create manifest
            manifest = ScriptManifest(
                fingerprint=fingerprint,
                prompt_sha=self._hash_prompt(request.prompt),
                context_sha=self._hash_context(request.context),
                language=request.language,
                entry="script.py",
                runtime={"python": "3.11"},
                deps=result["requirements"].split("\n") if result["requirements"] else [],
                allow={"network": result.get("metadata", {}).get("network", "requests" in result["requirements"]), "fs": []},
                template_version=self.template_version,
                outputs=result["outputs"]
            )
            
            return GenerationResponse(
                status="ok",
                script=result["script"],
                manifest=manifest,
                requirements=result["requirements"],
                readme=result["readme"]
            )
            
        except Exception as e:
            return GenerationResponse(
                status="error",
                script="",
                manifest=ScriptManifest(
                    fingerprint="",
                    prompt_sha="",
                    context_sha="",
                    language=request.language,
                    entry="script.py",
                    runtime={"python": "3.11"},
                    template_version=self.template_version
                ),
                requirements="",
                readme="",
                error=str(e)
            )
    
    def check_updates(self, request: UpdateRequest) -> UpdateResponse:
        """Check if a script needs updates."""
        # For now, always return no updates needed
        # In a real implementation, this would check for:
        # - New template versions
        # - Dependency updates
        # - Security vulnerabilities
        return UpdateResponse(
            needs_update=False,
            reason=None,
            new_fingerprint=None
        )
    
    def _generate_fingerprint(self, request: GenerationRequest) -> str:
        """Generate a fingerprint for the request."""
        content = f"{request.prompt}|{json.dumps(request.context, sort_keys=True)}|{request.language}|{self.template_version}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _hash_prompt(self, prompt: str) -> str:
        """Hash the normalized prompt."""
        normalized = prompt.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    def _hash_context(self, context: Dict[str, Any]) -> str:
        """Hash the normalized context."""
        normalized = json.dumps(context, sort_keys=True)
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
