from abc import ABC, abstractmethod
from typing import List

class OCREngine(ABC):
    @abstractmethod
    def extract(self, pdf_path: str, start_page: int) -> List[str]:
        pass
