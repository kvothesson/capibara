"""Capibara SDK client for script execution."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..core.service import CapibaraCore
from ..utils.fingerprint import generate_fingerprint
from ..utils.runner import ScriptRunner


class CapibaraResult:
    """Result object from script execution."""
    
    def __init__(self, data: Dict[str, Any]):
        self.status = data.get("status", "error")
        self.artifacts = data.get("artifacts", [])
        self.output = data.get("output", {})
        self.raw = data.get("raw", {})
        self._data = data
    
    def __getattr__(self, name: str) -> Any:
        """Allow access to output fields as attributes."""
        if name in self.output:
            return self.output[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __repr__(self) -> str:
        return f"CapibaraResult(status='{self.status}', artifacts={self.artifacts})"


class Capibara:
    """Main Capibara SDK client."""
    
    def __init__(self, work_dir: Optional[Union[str, Path]] = None, core_url: Optional[str] = None):
        self.work_dir = Path(work_dir) if work_dir else Path.cwd()
        self.cache_dir = self.work_dir / ".capibara" / "scripts"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize core service (in real implementation, this would be HTTP client)
        self.core = CapibaraCore()
        self.runner = ScriptRunner(self.work_dir)
    
    def run(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        select: Optional[List[str]] = None,
        refresh: bool = False,
        language: str = "python"
    ) -> CapibaraResult:
        """Run a script from a prompt and context."""
        if context is None:
            context = {}
        
        # Generate fingerprint
        fingerprint = generate_fingerprint(prompt, context, language)
        script_dir = self.cache_dir / fingerprint
        
        # Check if script exists in cache
        if not refresh and script_dir.exists() and (script_dir / "manifest.json").exists():
            return self._run_cached_script(script_dir, context, select)
        
        # Generate new script
        return self._generate_and_run_script(prompt, context, select, language, script_dir)
    
    def _run_cached_script(
        self,
        script_dir: Path,
        context: Dict[str, Any],
        select: Optional[List[str]] = None
    ) -> CapibaraResult:
        """Run a cached script."""
        try:
            # Load manifest
            manifest_path = script_dir / "manifest.json"
            if not manifest_path.exists():
                raise FileNotFoundError("Manifest not found")
            
            manifest = json.loads(manifest_path.read_text())
            
            # Run script
            script_path = script_dir / manifest["entry"]
            success, result, error = self.runner.run_script(script_path, context, manifest)
            
            if not success:
                return CapibaraResult({
                    "status": "error",
                    "message": result.get("message", "Script execution failed"),
                    "artifacts": [],
                    "output": {},
                    "raw": {"error": error}
                })
            
            # Apply field selection if requested
            if select and result.get("output"):
                filtered_output = {key: result["output"].get(key) for key in select}
                result["output"] = filtered_output
            
            return CapibaraResult(result)
            
        except Exception as e:
            return CapibaraResult({
                "status": "error",
                "message": f"Failed to run cached script: {str(e)}",
                "artifacts": [],
                "output": {},
                "raw": {"error": str(e)}
            })
    
    def _generate_and_run_script(
        self,
        prompt: str,
        context: Dict[str, Any],
        select: Optional[List[str]] = None,
        language: str = "python",
        script_dir: Path = None
    ) -> CapibaraResult:
        """Generate a new script and run it."""
        try:
            # Generate script using core service
            from ..core.models import GenerationRequest
            request = GenerationRequest(
                prompt=prompt,
                context=context,
                language=language
            )
            
            response = self.core.generate_script(request)
            
            if response.status != "ok":
                return CapibaraResult({
                    "status": "error",
                    "message": response.error or "Script generation failed",
                    "artifacts": [],
                    "output": {},
                    "raw": {"error": response.error}
                })
            
            # Create script directory
            if script_dir is None:
                fingerprint = generate_fingerprint(prompt, context, language)
                script_dir = self.cache_dir / fingerprint
            
            script_dir.mkdir(parents=True, exist_ok=True)
            
            # Save artifacts
            self._save_artifacts(script_dir, response)
            
            # Run the script
            script_path = script_dir / response.manifest.entry
            success, result, error = self.runner.run_script(script_path, context, response.manifest.model_dump())
            
            if not success:
                return CapibaraResult({
                    "status": "error",
                    "message": result.get("message", "Script execution failed"),
                    "artifacts": [],
                    "output": {},
                    "raw": {"error": error}
                })
            
            # Apply field selection if requested
            if select and result.get("output"):
                filtered_output = {key: result["output"].get(key) for key in select}
                result["output"] = filtered_output
            
            return CapibaraResult(result)
            
        except Exception as e:
            return CapibaraResult({
                "status": "error",
                "message": f"Failed to generate and run script: {str(e)}",
                "artifacts": [],
                "output": {},
                "raw": {"error": str(e)}
            })
    
    def _save_artifacts(self, script_dir: Path, response) -> None:
        """Save generated artifacts to the script directory."""
        # Save script
        script_path = script_dir / response.manifest.entry
        script_path.write_text(response.script)
        
        # Save manifest
        manifest_path = script_dir / "manifest.json"
        manifest_path.write_text(response.manifest.model_dump_json(indent=2))
        
        # Save requirements
        if response.requirements:
            requirements_path = script_dir / "requirements.txt"
            requirements_path.write_text(response.requirements)
        
        # Save README
        if response.readme:
            readme_path = script_dir / "README.md"
            readme_path.write_text(response.readme)
    
    def list_scripts(self) -> List[Dict[str, Any]]:
        """List all cached scripts."""
        scripts = []
        
        for script_dir in self.cache_dir.iterdir():
            if script_dir.is_dir():
                manifest_path = script_dir / "manifest.json"
                if manifest_path.exists():
                    try:
                        manifest = json.loads(manifest_path.read_text())
                        scripts.append({
                            "fingerprint": manifest["fingerprint"],
                            "prompt_sha": manifest["prompt_sha"],
                            "language": manifest["language"],
                            "created_at": manifest["created_at"],
                            "deps": manifest.get("deps", [])
                        })
                    except (json.JSONDecodeError, KeyError):
                        continue
        
        return scripts
    
    def clear_cache(self) -> None:
        """Clear all cached scripts."""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
