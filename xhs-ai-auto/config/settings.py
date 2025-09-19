import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the project root
load_dotenv()

# --- Google AI Configuration ---

# Gemini API for Text Generation
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash") # Default model

# Imagen API for Image Generation
IMAGEN_API_KEY = os.getenv("IMAGEN_API_KEY")
IMAGEN_MODEL_NAME = os.getenv("IMAGEN_MODEL_NAME", "imagen-3") # Default model

# --- Service Configuration ---

# Xiaohongshu MCP Service
XHS_MCP_BASE_URL = os.getenv("XHS_MCP_BASE_URL", "http://localhost:18060")
