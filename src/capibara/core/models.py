"""Data models for Capibara Core."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class GenerationRequest(BaseModel):
    """Request to generate a script from a prompt."""
    
    prompt: str = Field(..., description="Natural language prompt describing the task")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context data for the task")
    language: str = Field(default="python", description="Target programming language")
    template_version: str = Field(default="1.0.0", description="Template version to use")


class ScriptManifest(BaseModel):
    """Manifest for a generated script."""
    
    fingerprint: str = Field(..., description="Unique fingerprint for this script")
    prompt_sha: str = Field(..., description="SHA hash of normalized prompt")
    context_sha: str = Field(..., description="SHA hash of normalized context")
    language: str = Field(..., description="Programming language")
    entry: str = Field(..., description="Entry point file")
    runtime: Dict[str, str] = Field(..., description="Runtime requirements")
    deps: List[str] = Field(default_factory=list, description="Dependencies")
    allow: Dict[str, Union[bool, List[str]]] = Field(
        default_factory=lambda: {"network": False, "fs": []},
        description="Security permissions"
    )
    template_version: str = Field(..., description="Template version used")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    outputs: Dict[str, str] = Field(default_factory=dict, description="Expected output types")
    aliases: Dict[str, str] = Field(default_factory=dict, description="Field aliases")


class GenerationResponse(BaseModel):
    """Response from script generation."""
    
    status: str = Field(..., description="Generation status")
    script: str = Field(..., description="Generated script content")
    manifest: ScriptManifest = Field(..., description="Script manifest")
    requirements: str = Field(..., description="Requirements.txt content")
    readme: str = Field(..., description="README.md content")
    error: Optional[str] = Field(None, description="Error message if generation failed")


class UpdateRequest(BaseModel):
    """Request to check for script updates."""
    
    fingerprint: str = Field(..., description="Script fingerprint to check")
    current_deps: List[str] = Field(default_factory=list, description="Current dependencies")


class UpdateResponse(BaseModel):
    """Response from update check."""
    
    needs_update: bool = Field(..., description="Whether script needs update")
    reason: Optional[str] = Field(None, description="Reason for update")
    new_fingerprint: Optional[str] = Field(None, description="New fingerprint if update needed")
