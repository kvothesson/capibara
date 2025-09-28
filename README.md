# Capibara 🦫 – Technical Specification

[![GitHub](https://img.shields.io/github/v/release/kvothesson/capibara?style=flat-square)](https://github.com/kvothesson/capibara)
[![Python](https://img.shields.io/badge/python-3.11+-blue?style=flat-square)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/status-MVP-orange?style=flat-square)](https://github.com/kvothesson/capibara)

## 1. Overview
**Capibara** is a developer tool that converts natural language prompts into **executable scripts**, caches them inside the user’s repository, and runs them in a controlled environment.  

Unlike AI “code suggestion” tools, Capibara delivers **ready-to-run, reproducible artifacts** that:  
- Are generated **once** via LLM.  
- Are stored and versioned inside the repo (`.capibara/`).  
- Run **locally** without re-calling the LLM.  
- Can be updated only when dependencies change, errors occur, or new versions are available.  

**Tagline:** *“From idea to executable code, in one step.”*  

---

## 2. High-Level Architecture
### Components
1. **Capibara Core (SaaS service)**  
   - Endpoint `/gen`: prompt + context → script + manifest + requirements.  
   - Uses LLM with deterministic templates.  
   - Signs artifacts with hash + template version.  
   - Provides optional `/updates` endpoint to notify of invalidations (new deps, CVEs).  

2. **Capibara SDK (client library)**  
   - Entry point `capibara.run(prompt, context, select=None, refresh=False)`.  
   - Resolves fingerprint for `(prompt, context, template_version)`.  
   - Looks up cached script in `.capibara/scripts/<fingerprint>/`.  
   - Executes script in sandbox runner (`python_venv`, later Node/bash).  
   - Returns structured result (`artifacts`, `output`, `raw`).  

3. **Repository integration**  
   - Local cache of artifacts.  
   - Optionally commit artifacts (`.capibara/`) and open PRs when new/updated.  
   - Each script lives in a dedicated folder with manifest + code.  

---

## 3. Workflow
1. **First run**  
   - Developer calls `capibara.run("Concatenate two videos", ctx={...})`.  
   - SDK checks local cache. Not found → calls Core `/gen`.  
   - Core returns `script.py`, `manifest.json`, `requirements.txt`.  
   - SDK saves them under `.capibara/scripts/<fingerprint>/`.  
   - Script is executed in sandbox, outputs JSON.  
   - Results returned to user.  

2. **Subsequent runs**  
   - Fingerprint matches existing script.  
   - SDK runs local script only (no Core call).  

3. **Update/Invalidation**  
   - Triggered when:  
     - Dependency version changes (e.g., MoviePy 1.0.3 → 1.0.4).  
     - CVE or API breaking change.  
     - Script execution error categorized as fixable.  
   - SDK or Core generates new script → stored under new fingerprint.  
   - GitHub bot/CLI can open PR with diff.  

---

## 4. Artifact Structure
```
.capibara/
  scripts/
    <fingerprint>/
      manifest.json
      script.py
      requirements.txt
      README.md
```

### Example `manifest.json`
```json
{
  "fingerprint": "fp_a7c9d0...",
  "prompt_sha": "p_11ab...",
  "context_sha": "c_90ff...",
  "language": "python",
  "entry": "script.py",
  "runtime": {"python": "3.11"},
  "deps": ["moviepy==1.0.3"],
  "allow": {"network": false, "fs": ["./media"]},
  "template_version": "1.0.0",
  "created_at": "2025-09-28T14:22:10Z",
  "outputs": {
    "artifacts": "list[str]",
    "fps": "int?",
    "duration": "float?"
  },
  "aliases": {
    "precio": "price",
    "price_amount": "price"
  }
}
```

---

## 5. Script Contract
Every generated script must include:

1. **Header (front-matter in comments)**  
   Example:
   ```python
   # --- CAPIBARA ---
   # language: python
   # entry: script.py
   # deps: moviepy==1.0.3
   # network: false
   # template_version: 1.0.0
   # --- /CAPIBARA ---
   ```

2. **CLI interface**  
   - Accepts `--context` (inline JSON or `@file.json`).  
   - Accepts `--selftest` (imports & deps check).  
   - Optional `--dry-run` for validation without side effects.  

3. **Deterministic behavior**  
   - No random seeds unless fixed.  
   - File outputs named predictably.  

4. **Structured output**  
   - Final line must print JSON with at least:  
     ```json
     {
       "status": "ok|error",
       "artifacts": ["path1", "path2"],
       "output": {...}, 
       "raw": {...}
     }
     ```

---

## 6. SDK Usage Examples

### Example 1: Video concatenation (MoviePy)
```python
from capibara import Capibara

cb = Capibara()
res = cb.run(
    "Concatenate these videos with moviepy at 24fps",
    context={"inputs": ["intro.mp4", "clip.mp4"], "output": "final.mp4"}
)

print(res.artifacts)   # ["final.mp4"]
print(res.output.get("fps"), res.output.get("duration"))
```

### Example 2: Fetch item data from MercadoLibre
```python
res = cb.run(
    "Use MercadoLibre API to fetch price and description",
    context={"item_id": "MLA123456789"},
    select=["title", "price"]
)

print(res.output.title, res.output.price)
print(res.raw)  # Original fields as returned by API
```

---

## 7. Fingerprinting
Fingerprint = `hash(prompt_normalized + context_normalized + language + template_major_version)`

- **Normalization**:  
  - Prompt: lowercase, remove stopwords like “please”.  
  - Context: order keys, canonicalize types.  
- **Strict mode (MVP)**: path differences create new fingerprints.  
- **Future**: parametric mode, excluding irrelevant fields from hash.  

---

## 8. Security
- **Sandbox runner**: isolated venv, limited FS, network disabled by default.  
- **Allowlist imports**: only safe libraries allowed by template.  
- **Secrets**: read from ENV, never hardcoded in manifest/script.  
- **Path traversal** prevention: block `..` or symlinks outside workdir.  
- **Static checks**: lightweight regex scans for dangerous ops.  

---

## 9. Error Handling
- **Error taxonomy**:  
  - `ValidationError` (bad context).  
  - `DependencyError` (pip install failed).  
  - `NetworkError` (API unreachable).  
  - `ExecError` (runtime fail).  
  - `TemplateError` (LLM output invalid).  
- SDK surfaces clear messages + suggestions.  
- `refresh=True` can force regeneration with updated template.  

---

## 10. Installation & Usage

### Quick Start

1. **Clone and setup:**
   ```bash
   git clone https://github.com/kvothesson/capibara.git
   cd capibara
   ./setup_dev.sh
   source venv/bin/activate
   ```

2. **Test the installation:**
   ```bash
   python test_capibara.py
   ```

3. **Use the CLI:**
   ```bash
   capibara run "Concatenate these videos with moviepy at 24fps" --context '{"inputs": ["video1.mp4", "video2.mp4"], "output": "final.mp4"}'
   ```

4. **Use the Python SDK:**
   ```python
   from capibara import Capibara
   
   cb = Capibara()
   result = cb.run("Your prompt here", context={"key": "value"})
   print(result.artifacts)
   ```

### CLI Commands

- `capibara run <prompt>` - Run a script from a prompt
- `capibara list` - List cached scripts
- `capibara show <fingerprint>` - Show script details
- `capibara clear` - Clear script cache

### Examples

See the `examples/` directory for complete examples:
- `video_concat.py` - Video concatenation with MoviePy
- `mercadolibre_api.py` - MercadoLibre API integration

## 11. Roadmap
- **MVP (Q4 2025)** ✅  
  - Core `/gen` endpoint with LLM templates (Python only).  
  - SDK Python (`run`, fingerprint cache, sandbox runner).  
  - Video concat + MercadoLibre API examples.

- **Next (Q1 2026)**  
  - Node.js SDK.  
  - CLI (`capibara run`, `capibara update`).  
  - PR bot for GitHub/GitLab.

- **Later**  
  - Support for Bash, JS, and workflows (multi-step).  
  - Shared cloud cache of fingerprints/artifacts.  
  - Marketplace of templates/capabilities.
