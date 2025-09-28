"""Capibara CLI main entry point."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from ..sdk.client import Capibara


console = Console()


@click.group()
@click.option("--work-dir", "-w", type=click.Path(exists=True, file_okay=False), help="Working directory")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def cli(ctx, work_dir: Optional[str], verbose: bool):
    """Capibara - From idea to executable code, in one step."""
    ctx.ensure_object(dict)
    ctx.obj["work_dir"] = Path(work_dir) if work_dir else Path.cwd()
    ctx.obj["verbose"] = verbose


@cli.command()
@click.argument("prompt")
@click.option("--context", "-c", help="Context as JSON string or @file.json")
@click.option("--select", "-s", multiple=True, help="Select specific output fields")
@click.option("--refresh", "-r", is_flag=True, help="Force regeneration")
@click.option("--language", "-l", default="python", help="Programming language")
@click.pass_context
def run(ctx, prompt: str, context: Optional[str], select: tuple, refresh: bool, language: str):
    """Run a script from a prompt."""
    work_dir = ctx.obj["work_dir"]
    verbose = ctx.obj["verbose"]
    
    # Parse context
    context_data = {}
    if context:
        if context.startswith("@"):
            # Read from file
            context_file = Path(context[1:])
            if not context_file.exists():
                console.print(f"[red]Error: Context file not found: {context_file}[/red]")
                sys.exit(1)
            context_data = json.loads(context_file.read_text())
        else:
            # Parse JSON string
            try:
                context_data = json.loads(context)
            except json.JSONDecodeError as e:
                console.print(f"[red]Error: Invalid JSON context: {e}[/red]")
                sys.exit(1)
    
    # Initialize Capibara
    capibara = Capibara(work_dir=work_dir)
    
    if verbose:
        console.print(f"[blue]Running prompt:[/blue] {prompt}")
        console.print(f"[blue]Context:[/blue] {json.dumps(context_data, indent=2)}")
    
    # Run script
    result = capibara.run(
        prompt=prompt,
        context=context_data,
        select=list(select) if select else None,
        refresh=refresh,
        language=language
    )
    
    # Display results
    if result.status == "ok":
        console.print("[green]✓ Script executed successfully[/green]")
        
        if result.artifacts:
            console.print(f"[blue]Artifacts created:[/blue] {', '.join(result.artifacts)}")
        
        if result.output:
            console.print("\n[blue]Output:[/blue]")
            console.print(json.dumps(result.output, indent=2))
        
        if verbose and result.raw:
            console.print("\n[blue]Raw data:[/blue]")
            console.print(json.dumps(result.raw, indent=2))
    else:
        console.print(f"[red]✗ Script failed: {result.output.get('message', 'Unknown error')}[/red]")
        if verbose and result.raw:
            console.print(f"[red]Details:[/red] {json.dumps(result.raw, indent=2)}")
        sys.exit(1)


@cli.command()
@click.pass_context
def list(ctx):
    """List cached scripts."""
    work_dir = ctx.obj["work_dir"]
    
    capibara = Capibara(work_dir=work_dir)
    scripts = capibara.list_scripts()
    
    if not scripts:
        console.print("[yellow]No cached scripts found[/yellow]")
        return
    
    # Create table
    table = Table(title="Cached Scripts")
    table.add_column("Fingerprint", style="cyan")
    table.add_column("Language", style="green")
    table.add_column("Created", style="blue")
    table.add_column("Dependencies", style="magenta")
    
    for script in scripts:
        deps_str = ", ".join(script["deps"][:3])
        if len(script["deps"]) > 3:
            deps_str += "..."
        
        table.add_row(
            script["fingerprint"][:12] + "...",
            script["language"],
            script["created_at"][:10],
            deps_str or "None"
        )
    
    console.print(table)


@cli.command()
@click.argument("fingerprint")
@click.pass_context
def show(ctx, fingerprint: str):
    """Show details of a cached script."""
    work_dir = ctx.obj["work_dir"]
    
    capibara = Capibara(work_dir=work_dir)
    script_dir = capibara.cache_dir / fingerprint
    
    if not script_dir.exists():
        console.print(f"[red]Script not found: {fingerprint}[/red]")
        sys.exit(1)
    
    # Load manifest
    manifest_path = script_dir / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        
        # Display manifest
        console.print(Panel(
            json.dumps(manifest, indent=2),
            title="Manifest",
            border_style="blue"
        ))
    
    # Display script
    script_path = script_dir / "script.py"
    if script_path.exists():
        script_content = script_path.read_text()
        syntax = Syntax(script_content, "python", theme="monokai", line_numbers=True)
        console.print(Panel(
            syntax,
            title="Script",
            border_style="green"
        ))


@cli.command()
@click.pass_context
def clear(ctx):
    """Clear all cached scripts."""
    work_dir = ctx.obj["work_dir"]
    
    capibara = Capibara(work_dir=work_dir)
    capibara.clear_cache()
    
    console.print("[green]✓ Cache cleared[/green]")


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
