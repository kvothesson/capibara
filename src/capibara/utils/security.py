"""Security utilities for script execution."""

import ast
import re
from pathlib import Path
from typing import List, Set, Dict, Any


class SecurityManager:
    """Manages security policies for script execution."""
    
    def __init__(self):
        self.allowed_imports = {
            # Standard library
            "json", "sys", "os", "pathlib", "datetime", "time", "math", "random",
            "collections", "itertools", "functools", "operator", "re", "string",
            "urllib", "http", "base64", "hashlib", "uuid", "tempfile", "shutil",
            "zipfile", "tarfile", "csv", "xml", "html", "email", "logging",
            "subprocess", "threading", "multiprocessing", "queue", "socket",
            "ssl", "gzip", "bz2", "lzma", "pickle", "copy", "warnings",
            
            # Common data science libraries
            "numpy", "pandas", "matplotlib", "seaborn", "scipy", "sklearn",
            
            # Common web libraries
            "requests", "urllib3", "httpx",
            
            # Common video/image libraries
            "moviepy", "PIL", "opencv", "cv2",
            
            # Common file formats
            "yaml", "toml", "configparser", "argparse", "click",
        }
        
        self.blocked_patterns = [
            r"__import__\s*\(",
            r"exec\s*\(",
            r"eval\s*\(",
            r"compile\s*\(",
            r"open\s*\(\s*['\"][^'\"]*\.\./",
            r"open\s*\(\s*['\"][^'\"]*\.\.\\",
            r"subprocess\.run\s*\(",
            r"os\.system\s*\(",
            r"os\.popen\s*\(",
            r"os\.exec\w*\s*\(",
            r"os\.spawn\w*\s*\(",
            r"os\.fork\s*\(",
            r"os\.kill\s*\(",
            r"os\.remove\s*\(",
            r"os\.unlink\s*\(",
            r"os\.rmdir\s*\(",
            r"os\.removedirs\s*\(",
            r"shutil\.rmtree\s*\(",
            r"shutil\.move\s*\(",
            r"shutil\.copy\s*\(",
            r"shutil\.copytree\s*\(",
        ]
    
    def validate_script(self, script: str, manifest: Dict[str, Any]) -> List[str]:
        """Validate a script for security issues."""
        errors = []
        
        # Check for blocked patterns
        for pattern in self.blocked_patterns:
            if re.search(pattern, script, re.IGNORECASE):
                errors.append(f"Blocked pattern detected: {pattern}")
        
        # Check imports
        try:
            tree = ast.parse(script)
            imports = self._extract_imports(tree)
            
            for import_name in imports:
                if not self._is_import_allowed(import_name, manifest):
                    errors.append(f"Import not allowed: {import_name}")
                    
        except SyntaxError as e:
            errors.append(f"Syntax error in script: {e}")
        
        return errors
    
    def _extract_imports(self, tree: ast.AST) -> Set[str]:
        """Extract all import statements from AST."""
        imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
        
        return imports
    
    def _is_import_allowed(self, import_name: str, manifest: Dict[str, Any]) -> bool:
        """Check if an import is allowed based on manifest."""
        # Check if import is in allowed list
        if import_name in self.allowed_imports:
            return True
        
        # Check if import is in dependencies
        deps = manifest.get("deps", [])
        for dep in deps:
            if import_name in dep.lower():
                return True
        
        return False
    
    def validate_file_access(self, file_path: str, work_dir: Path) -> bool:
        """Validate that file access is within allowed directory."""
        try:
            # Resolve the path
            resolved_path = work_dir / file_path
            resolved_path = resolved_path.resolve()
            
            # Check if path is within work directory
            return work_dir.resolve() in resolved_path.parents or resolved_path == work_dir.resolve()
            
        except (OSError, ValueError):
            return False
    
    def create_sandbox_environment(self, work_dir: Path, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Create a sandbox environment for script execution."""
        env = {
            "PYTHONPATH": str(work_dir),
            "CAPIBARA_WORK_DIR": str(work_dir),
            "CAPIBARA_NETWORK_ALLOWED": str(manifest.get("allow", {}).get("network", False)),
        }
        
        # Add allowed file system paths
        fs_allowed = manifest.get("allow", {}).get("fs", [])
        if fs_allowed:
            env["CAPIBARA_FS_ALLOWED"] = ":".join(fs_allowed)
        
        return env
