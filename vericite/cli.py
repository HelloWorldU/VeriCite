import typer
import sys
import os

# Suppress PaddleOCR welcome message and warnings - MUST BE BEFORE OTHER IMPORTS
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
# Suppress specific Paddle warnings
os.environ["FLAGS_allocator_strategy"] = 'auto_growth' 

from vericite.core.slicer import smart_slice
from vericite.core.ocr.local import LocalEngine
from vericite.core.ocr.cloud import CloudEngine
from vericite.core.validator import validate_citations
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Disable pretty exceptions to avoid the crash in error handling
app = typer.Typer(help="VeriCite: Academic Citation Integrity Checker", pretty_exceptions_enable=False)
console = Console()

# Suppress PaddleOCR welcome message and warnings
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
# Redirect stderr to suppress other Paddle warnings during init if needed
# (Not doing full redirect here to avoid hiding real errors, but env var handles the main one)

# Interactive REPL mode
@app.command()
def main():
    """
    Start VeriCite in interactive mode (Claude Code style).
    """
    # Clear screen for a fresh start
    # os.system('cls' if os.name == 'nt' else 'clear')
    
    # 1. Mock Login / Welcome Banner
    # Create a more stylish layout
    from rich.align import Align
    from rich.text import Text
    
    title = Text("VeriCite AI", style="bold cyan", justify="center")
    subtitle = Text("Context-Aware Verification for the AI Era", style="dim cyan", justify="center")
    
    console.print(Panel(
        Align.center(title + "\n" + subtitle),
        border_style="cyan",
        padding=(1, 2)
    ))
    
    with console.status("[bold green]Authenticating...[/bold green]", spinner="dots"):
        import time
        time.sleep(0.8) # Mock network delay
    
    console.print("[green]✓ Authenticated as[/green] [bold]User[/bold]")
    console.print("[dim]Type 'exit' or 'quit' to leave.[/dim]\n")

    # 2. Main Loop
    while True:
        try:
            # Styled prompt
            user_input = console.input("[bold cyan]➜[/bold cyan] ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit"]:
                console.print("[yellow]Goodbye![/yellow]")
                break
                
            # 3. Smart Input Handling
            # Case A: File Path (PDF or TXT)
            if os.path.exists(user_input) and os.path.isfile(user_input):
                file_ext = os.path.splitext(user_input)[1].lower()
                
                if file_ext == ".pdf":
                    # Delegate to PDF scan logic
                    process_pdf(user_input)
                else:
                    # Treat as text file
                    process_text_file(user_input)
                    
            # Case B: Raw Text (Citation string)
            else:
                # Assume raw text if it looks like a citation or is long enough
                if len(user_input) > 10:
                    process_raw_text(user_input)
                else:
                    console.print("[red]Input not found as file and too short to be a citation.[/red]")

        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

def process_pdf(path: str):
    console.print(f"[dim]Analyzing PDF: {path}[/dim]")
    # Reuse existing scan logic (simplified)
    with console.status("Processing PDF...", spinner="dots"):
        ref_page = smart_slice(path)
        if ref_page == -1: 
            ref_page = 0 # Fallback
            
        # Try local engine (which now has auto-fallback)
        engine = LocalEngine()
        citations = engine.extract(path, ref_page)
        
    if not citations:
        console.print("[red]No citations found.[/red]")
        return
        
    _validate_and_report(citations)

def process_text_file(path: str):
    console.print(f"[dim]Reading text file: {path}[/dim]")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    process_raw_text(text)

def process_raw_text(text: str):
    citations = [line.strip() for line in text.split('\n') if len(line.strip()) > 10]
    if not citations:
        console.print("[red]No valid citations parsed.[/red]")
        return
    _validate_and_report(citations)

def _validate_and_report(citations):
    console.print(f"Found {len(citations)} candidate citations.")
    with console.status("Verifying...", spinner="dots"):
        results = validate_citations(citations)
    
    # Simple report for REPL
    for res in results:
        icon = "✅" if res["valid"] else "❌"
        color = "green" if res["valid"] else "red"
        console.print(f"[{color}]{icon} {res['text'][:80]}... ({res.get('doi') or res.get('reason')})[/{color}]")
    console.print("") # Newline

if __name__ == "__main__":
    # If no args provided, run interactive mode
    if len(sys.argv) == 1:
        main()
    else:
        app()
