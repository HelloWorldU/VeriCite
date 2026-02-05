from typing import List
from .engine import OCREngine

class CloudEngine(OCREngine):
    def extract(self, pdf_path: str, start_page: int) -> List[str]:
        # Placeholder for DeepSeek/GLM API
        print(f"Uploading {pdf_path} pages {start_page}+ to Cloud API...")
        return ["Cloud Result 1: Deep Learning (2024)", "Cloud Result 2: Transformer (2017)"]
