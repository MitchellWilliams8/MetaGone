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

@app.command()
def clean(
   file_path: Path = typer.Argument(
       ..., help="Path to the file you want to sanitize"
   ),
   output: Path = typer.Option(
       None, "--output", "-o", help="Custom destination path"
   ),
):
   """Sanitize a file by stripping metadata."""
   if not file_path.exists():
       console.print(
           f"[bold red]Error:[/bold red] File '{file_path}' does not exist."
       )
       raise typer.Exit(code=1)

   dest = (
       output
       if output
       else file_path.parent / f"cleaned_{file_path.stem}{file_path.suffix}"
   )

   ext = file_path.suffix.lower()
   if ext in [".jpg", ".jpeg", ".png"]:
       result = scrub_image(file_path, dest)
   elif ext == ".docx":
       result = scrub_docx(file_path, dest)
   elif ext == ".pdf":
       result = scrub_pdf(file_path, dest)
   else:
       console.print(
           f"[yellow]Format '{ext}' not yet supported."
       )
       raise typer.Exit()

   table = Table(title="Sanitization Report")
   table.add_column("File", style="cyan")
   table.add_column("Type", style="magenta")
   table.add_column("Metadata Found?", style="green")
   table.add_column("Result", style="bold green")

   table.add_row(
       result["file"],
       result["type"],
       str(result["metadata_detected"]),
       f"Saved to {dest.name}",
   )

   console.print(table)

if __name__ == "__main__":
   app()
