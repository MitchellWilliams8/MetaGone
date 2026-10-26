from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table

from MetaGone.modules.image import scrub_image
from MetaGone.modules.docx import scrub_docx
from MetaGone.modules.pdf import scrub_pdf

app = typer.Typer(
   help="MetaGone: A command line tool for removing metadata from files."
)
console = Console()

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".docx", ".pdf"}

@app.callback()
def main():
    """MetaGone privacy tool."""
    pass

def collect_target_files(target: Path) -> list[Path]:
    """Resolves target into a list of supported files whether given a file or directory."""
    if target.is_file():
        return [target] if target.suffix.lower() in SUPPORTED_EXTENSIONS else []
    elif target.is_dir():
        return [
            p
            for p in target.rglob("*")
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
        ]
    return []

@app.command()
def clean(
    target_path: Path = typer.Argument(
        ..., help="Path to a single file or a directory to sanitize"
    ),
    output: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="Custom destination directory or file path",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-d",
        help="Inspect and report metadata without saving changes",
    ),
):
    """Sanitize individual files or recursively scan entire directories."""
    if not target_path.exists():
        console.print(
            f"[bold red]Error:[/bold red] Target path '{target_path}' does not exist."
        )
        raise typer.Exit(code=1)

    files_to_process = collect_target_files(target_path)

    if not files_to_process:
        console.print(
            f"[yellow]No supported files found at '{target_path}'.[/yellow]"
        )
        console.print(
            f"Supported extensions: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )
        raise typer.Exit()

    mode_label = (
        "[bold yellow]DRY RUN (Audit Only)[/bold yellow]"
        if dry_run
        else "[bold green]LIVE CLEAN[/bold green]"
    )
    table = Table(title=f"MetaGone Report — {mode_label}")
    table.add_column("File", style="cyan")
    table.add_column("Format", style="magenta")
    table.add_column("Metadata Found?", style="bold")
    table.add_column("Action Taken", style="green")

    leaks_found_count = 0

    for file in files_to_process:
        ext = file.suffix.lower()

        if dry_run:
            dest = None
        elif output and target_path.is_file() and not output.is_dir():
            dest = output
        elif output and output.is_dir():
            dest = output / f"cleaned_{file.name}"
        else:
            dest = file.parent / f"cleaned_{file.name}"

        if ext in [".jpg", ".jpeg", ".png", ".webp"]:
            result = scrub_image(file, dest if not dry_run else file)
        elif ext == ".docx":
            result = scrub_docx(file, dest if not dry_run else file)
        elif ext == ".pdf":
            result = scrub_pdf(file, dest if not dry_run else file)

        if dry_run and dest and dest.exists() and dest != file:
            dest.unlink()

        has_meta = result.get("metadata_detected", False)
        if has_meta:
            leaks_found_count += 1

        meta_status = "[red]YES (Leak)[/red]" if has_meta else "[green]NO[/green]"
        action = (
            "[yellow]Inspected (No Write)[/yellow]"
            if dry_run
            else f"Saved -> {dest.name}"
        )

        table.add_row(file.name, result["type"], meta_status, action)

    console.print(table)
    console.print(
        f"\n[bold]Summary:[/bold] Scanned [cyan]{len(files_to_process)}[/cyan] files | Leaks detected: [red]{leaks_found_count}[/red]"
    )

if __name__ == "__main__":
    app()
