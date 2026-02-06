import os

# Suppress PaddleOCR welcome message and warnings - MUST BE BEFORE OTHER IMPORTS
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
# Suppress specific Paddle warnings
os.environ["FLAGS_allocator_strategy"] = 'auto_growth' 

__version__ = "0.1.0"
