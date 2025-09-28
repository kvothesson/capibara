"""Script runner for executing generated scripts safely."""

import json
import subprocess
import tempfile
import venv
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import sys
import os


class ScriptRunner:
    """Runs scripts in a sandboxed environment."""
    
    def __init__(self, work_dir: Optional[Path] = None):
        self.work_dir = work_dir or Path.cwd()
        self.security_manager = None  # Will be imported when needed
    
    def run_script(
        self,
        script_path: Path,
        context: Dict[str, Any],
        manifest: Dict[str, Any],
        timeout: int = 300
    ) -> Tuple[bool, Dict[str, Any], str]:
        """Run a script with the given context and manifest."""
        try:
            # Import security manager here to avoid circular imports
            from .security import SecurityManager
            self.security_manager = SecurityManager()
            
            # Validate script security
            script_content = script_path.read_text()
            security_errors = self.security_manager.validate_script(script_content, manifest)
            
            if security_errors:
                return False, {
                    "status": "error",
                    "message": "Security validation failed",
                    "errors": security_errors
                }, ""
            
            # Create temporary directory for execution
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Copy script to temp directory
                script_name = script_path.name
                temp_script = temp_path / script_name
                temp_script.write_text(script_content)
                
                # Install dependencies if any
                deps = manifest.get("deps", [])
                if deps:
                    self._install_dependencies(temp_path, deps)
                
                # Prepare environment
                env = self._prepare_environment(temp_path, manifest)
                
                # Run script
                result = self._execute_script(
                    temp_script,
                    context,
                    env,
                    timeout
                )
                
                return True, result, ""
                
        except Exception as e:
            return False, {
                "status": "error",
                "message": f"Execution failed: {str(e)}"
            }, str(e)
    
    def _install_dependencies(self, work_dir: Path, deps: List[str]) -> None:
        """Install dependencies in a virtual environment."""
        if not deps:
            return
        
        # Create virtual environment
        venv_path = work_dir / "venv"
        venv.create(venv_path, with_pip=True)
        
        # Get pip path
        if sys.platform == "win32":
            pip_path = venv_path / "Scripts" / "pip"
        else:
            pip_path = venv_path / "bin" / "pip"
        
        # Install dependencies
        try:
            subprocess.run(
                [str(pip_path), "install"] + deps,
                cwd=work_dir,
                check=True,
                capture_output=True,
                timeout=60
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to install dependencies: {e.stderr.decode()}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Dependency installation timed out")
    
    def _prepare_environment(self, work_dir: Path, manifest: Dict[str, Any]) -> Dict[str, str]:
        """Prepare environment variables for script execution."""
        env = os.environ.copy()
        
        # Set work directory
        env["CAPIBARA_WORK_DIR"] = str(work_dir)
        
        # Set network permissions
        network_allowed = manifest.get("allow", {}).get("network", False)
        env["CAPIBARA_NETWORK_ALLOWED"] = str(network_allowed)
        
        # Set file system permissions
        fs_allowed = manifest.get("allow", {}).get("fs", [])
        if fs_allowed:
            env["CAPIBARA_FS_ALLOWED"] = ":".join(fs_allowed)
        
        # Add virtual environment to PATH if it exists
        venv_path = work_dir / "venv"
        if venv_path.exists():
            if sys.platform == "win32":
                venv_bin = venv_path / "Scripts"
            else:
                venv_bin = venv_path / "bin"
            
            if venv_bin.exists():
                env["PATH"] = str(venv_bin) + os.pathsep + env["PATH"]
        
        return env
    
    def _execute_script(
        self,
        script_path: Path,
        context: Dict[str, Any],
        env: Dict[str, str],
        timeout: int
    ) -> Dict[str, Any]:
        """Execute the script with the given context."""
        # Prepare command
        if sys.platform == "win32":
            python_cmd = "python"
        else:
            python_cmd = "python3"
        
        cmd = [python_cmd, str(script_path), json.dumps(context)]
        
        try:
            # Run script
            result = subprocess.run(
                cmd,
                cwd=script_path.parent,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Parse output
            if result.stdout:
                try:
                    # Try to parse JSON from last line
                    lines = result.stdout.strip().split('\n')
                    last_line = lines[-1]
                    output = json.loads(last_line)
                    return output
                except json.JSONDecodeError:
                    # If not JSON, return raw output
                    return {
                        "status": "ok",
                        "artifacts": [],
                        "output": {"raw_output": result.stdout},
                        "raw": {"stdout": result.stdout, "stderr": result.stderr}
                    }
            else:
                return {
                    "status": "error",
                    "message": "No output from script",
                    "raw": {"stdout": result.stdout, "stderr": result.stderr}
                }
                
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "Script execution timed out"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Execution error: {str(e)}"
            }
