from typing import List
from .engine import OCREngine
import fitz
from rich.console import Console

console = Console()

try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None

class LocalEngine(OCREngine):
    def __init__(self):
        # We delay OCR initialization to until it's actually needed
        # But we check availability here
        self.ocr_available = PaddleOCR is not None
        self.ocr_model = None

    def _init_ocr(self):
        if self.ocr_model:
            return
        
        if not self.ocr_available:
            return

        try:
            # use_angle_cls=True need to download model
            # lang="en" covers English, but Paddle supports chinese_cht too
            # NOTE: PaddleOCR v3+ changed 'show_log' to logger config or removed it from init args in some versions
            try:
                self.ocr_model = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
            except ValueError:
                 # Fallback for newer PaddleOCR versions that might reject show_log
                self.ocr_model = PaddleOCR(use_angle_cls=True, lang="en")
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to initialize PaddleOCR ({e}). Will rely on text extraction only.[/yellow]")
            self.ocr_available = False

    def extract(self, pdf_path: str, start_page: int) -> List[str]:
        """
        Extract citations from the PDF starting at start_page.
        Strategy:
        1. Try direct text extraction (PyMuPDF) - Fast & Accurate for digital PDFs
        2. If text layer is empty/garbage -> Fallback to PaddleOCR (if available)
        """
        citations = []
        doc = fitz.open(pdf_path)
        total_pages = len(doc)

        for page_num in range(start_page, total_pages):
            page = doc[page_num]
            
            # --- Strategy 1: Direct Text Extraction ---
            text = page.get_text()
            
            # IMPROVED LOGIC: Check for meaningful content, not just length
            # If we extracted anything that looks like alphanumeric text, use it.
            # Only fallback to OCR if text is practically empty or whitespace.
            if text and len(text.strip()) > 5:  # Lower threshold to 5 chars to catch single short citations
                # Naive splitting by newline. 
                # TODO: Implement better citation splitting logic (e.g. looking for [1], [2])
                lines = text.split('\n')
                # Filter out extremely short lines (page numbers) but keep potential short citations
                page_citations = [l.strip() for l in lines if len(l.strip()) > 10]
                citations.extend(page_citations)
                continue
            
            # --- Strategy 2: OCR Fallback ---
            console.print(f"[yellow]Page {page_num+1} seems to be an image. Attempting OCR...[/yellow]")
            
            # Initialize OCR only if needed
            self._init_ocr()
            
            if self.ocr_model:
                try:
                    # 1. Render page to image
                    pix = page.get_pixmap(dpi=300)
                    img_data = pix.tobytes("png") 
                    
                    # 2. Run OCR
                    result = self.ocr_model.ocr(img_data, cls=True)
                    
                    # 3. Post-process
                    if result and result[0]:
                        page_text_blocks = []
                        for line in result[0]:
                            box, (txt, score) = line
                            if score > 0.5:
                                page_text_blocks.append(txt)
                        citations.extend(page_text_blocks)
                except Exception as e:
                    console.print(f"[red]OCR Failed for page {page_num+1}: {e}[/red]")
            else:
                console.print(f"[red]Skipping page {page_num+1}: No text layer and OCR not available.[/red]")

        if not citations:
             # If we still have nothing, maybe return a hint or empty list
             return []
             
        return citations
