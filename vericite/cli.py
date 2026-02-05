import typer
import sys
import os
from typing_extensions import Annotated
from vericite.core.slicer import smart_slice
from vericite.core.ocr.local import LocalEngine
from vericite.core.ocr.cloud import CloudEngine
from vericite.core.validator import validate_citations
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

app = typer.Typer(help="VeriCite: Academic Citation Integrity Checker")
console = Console()

@app.command()
def scan(
    pdf_path: str = typer.Argument(..., help="Path to the PDF file to check"),
    engine: Annotated[str, typer.Option(help="OCR Engine: local or cloud")] = "local"
):
    """
    Scan a PDF for fake citations using Local (PaddleOCR) or Cloud (DeepSeek/GLM) engines.
    """
    if not os.path.exists(pdf_path):
        console.print(f"[bold red]Error:[/bold red] File not found: {pdf_path}")
        raise typer.Exit(code=1)

    console.print(Panel.fit(f"[bold cyan]VeriCite Scanner[/bold cyan]\nTarget: {pdf_path}\nEngine: {engine}", border_style="cyan"))

    # 1. Smart Slicing
    with console.status("[bold green]🔍 Phase 1: Locating References Section...[/bold green]", spinner="dots"):
        ref_page_index = smart_slice(pdf_path)
    
    if ref_page_index == -1:
        console.print("[yellow]⚠️  Could not automatically find 'References' section.[/yellow]")
        console.print("Defaulting to scanning the last 3 pages.")
        # Fallback to last few pages if file is large enough
        import fitz
        doc = fitz.open(pdf_path)
        ref_page_index = max(0, len(doc) - 3)
    else:
        console.print(f"✅ References found starting at page: [bold]{ref_page_index + 1}[/bold]")

    # 2. OCR Processing
    ocr_engine = LocalEngine() if engine == "local" else CloudEngine()
    
    with console.status(f"[bold green]📖 Phase 2: Extracting Citations ({engine})...[/bold green]", spinner="dots"):
        try:
            raw_citations = ocr_engine.extract(pdf_path, start_page=ref_page_index)
        except Exception as e:
            console.print(f"[bold red]OCR Error:[/bold red] {e}")
            raise typer.Exit(code=1)
    
    console.print(f"✅ Extracted {len(raw_citations)} candidate citations.")

    if not raw_citations:
        console.print("[red]No text extracted. Is the PDF scanned? Try --engine cloud[/red]")
        raise typer.Exit()

    # 3. Validation
    with console.status("[bold green]🕵️  Phase 3: Verifying against Crossref Database...[/bold green]", spinner="dots"):
        results = validate_citations(raw_citations)

    # 4. Report
    table = Table(title="Verification Report", show_header=True, header_style="bold magenta")
    table.add_column("Status", style="dim", width=8)
    table.add_column("Citation Text", width=60)
    table.add_column("DOI / Note", justify="right")

    valid_count = 0
    hallucination_count = 0

    for res in results:
        if res["valid"]:
            valid_count += 1
            status = "[green]PASS[/green]"
            doi = res.get('doi') or "Verified"
        else:
            hallucination_count += 1
            status = "[red]FAIL[/red]"
            doi = res.get('reason', 'Unknown')
            
        table.add_row(status, res['text'][:100] + "..." if len(res['text'])>100 else res['text'], doi)

    console.print(table)
    
    # Summary
    console.print("\n[bold]Summary:[/bold]")
    console.print(f"🟢 Verified: {valid_count}")
    console.print(f"🔴 Potentially Fake/Unverified: {hallucination_count}")
    
    if hallucination_count > 0:
        console.print("\n[italic yellow]Tip: Some 'Fail' results might be due to OCR errors or formatting issues.[/italic yellow]")
        if engine == "local":
             console.print("[italic cyan]Try using --engine cloud for higher accuracy on scanned documents.[/italic cyan]")

if __name__ == "__main__":
    app()
