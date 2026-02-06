from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

import os

def create_test_pdf(filename):
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Page 1: Some random content
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "AI Generated Paper on Quantum Biology")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, "Abstract: This is a generated paper to test VeriCite.")
    c.drawString(50, height - 100, "It contains both real and fake citations.")
    c.showPage()

    # Page 2: References
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "References")
    
    c.setFont("Helvetica", 10)
    y_position = height - 80

    # 1. Real Citation (Should PASS)
    # Vaswani et al. "Attention Is All You Need"
    real_citation = "1. Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., ... & Polosukhin, I. (2017). Attention is all you need. Advances in neural information processing systems, 30."
    c.drawString(50, y_position, real_citation)
    y_position -= 30

    # 2. Fake Citation (AI Hallucination) (Should FAIL)
    # A completely made up paper combining real terms
    fake_citation_1 = "2. Smith, J. D., & Johnson, T. (2025). Quantum Entanglement in Large Language Models. Journal of Artificial General Intelligence, 12(4), 112-145."
    c.drawString(50, y_position, fake_citation_1)
    y_position -= 30

    # 3. Real Citation (Should PASS)
    # ResNet paper
    real_citation_2 = "3. He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep residual learning for image recognition. In Proceedings of the IEEE conference on computer vision and pattern recognition (pp. 770-778)."
    c.drawString(50, y_position, real_citation_2)
    y_position -= 30

    # 4. Fake Citation (Subtle Hallucination) (Should FAIL)
    # Real authors, real journal, but fake paper title/year combo
    fake_citation_2 = "4. LeCun, Y., & Hinton, G. (2023). The End of Backpropagation: A New Era. Nature Machine Intelligence, 5, 20-30."
    c.drawString(50, y_position, fake_citation_2)
    y_position -= 30

    c.save()
    print(f"Created {filename}")

if __name__ == "__main__":
    create_test_pdf("tests/fixtures/test_ai_hallucination.pdf")
