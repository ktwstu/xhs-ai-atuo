import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the project root
load_dotenv()

# === AI Provider Selection ===
# Options: google, modelscope, dashscope
AI_PROVIDER = os.getenv("AI_PROVIDER", "google")

# === Google AI Configuration (existing) ===

# Gemini API for Text Generation
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash") # Default model

# Imagen API for Image Generation
IMAGEN_API_KEY = os.getenv("IMAGEN_API_KEY")
IMAGEN_MODEL_NAME = os.getenv("IMAGEN_MODEL_NAME", "imagen-4.0-fast-generate-001") # Default model

# === ModelScope API-Inference Configuration (new) ===
# 2000 free API calls per day
MODELSCOPE_API_KEY = os.getenv("MODELSCOPE_API_KEY")
MS_TEXT_MODEL = os.getenv("MS_TEXT_MODEL", "Qwen/Qwen2.5-Coder-32B-Instruct")
MS_IMAGE_MODEL = os.getenv("MS_IMAGE_MODEL", "Qwen/Qwen-Image")  # Use FLUX for image generation
MS_ENABLE_THINKING = os.getenv("MS_ENABLE_THINKING", "false").lower() == "true"

# === DashScope/Alibaba Cloud Configuration (new) ===
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
QIANWEN_MODEL_NAME = os.getenv("QIANWEN_MODEL_NAME", "qwen-plus")
WANXIANG_MODEL_NAME = os.getenv("WANXIANG_MODEL_NAME", "qwen-image")  # or "wanx-v1"

# === Service Configuration ===

# Xiaohongshu MCP Service
XHS_MCP_BASE_URL = os.getenv("XHS_MCP_BASE_URL", "http://localhost:18060")
