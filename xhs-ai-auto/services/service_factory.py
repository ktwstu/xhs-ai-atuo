"""
Service factory for creating AI service instances.
Supports dynamic switching between different AI providers.
"""

from typing import Optional
from config import settings
from services.ai_service import AIService


def get_ai_service() -> AIService:
    """
    Get an AI service instance based on configuration.

    Returns:
        AIService instance based on AI_PROVIDER setting

    Raises:
        ValueError: If the specified provider is not supported
    """
    provider = settings.AI_PROVIDER.lower()
    print(f"[INFO] Initializing AI service: {provider}")

    if provider == "google":
        from services.google_service import GoogleAIService
        service = GoogleAIService()
        if service.is_available():
            return service
        else:
            print("[WARNING] Google service not available, trying fallback...")
            provider = "modelscope"  # Fallback to ModelScope

    if provider == "modelscope":
        from services.modelscope_service import ModelScopeAIService
        service = ModelScopeAIService()
        if service.is_available():
            return service
        else:
            print("[WARNING] ModelScope service not available, trying DashScope...")
            provider = "dashscope"  # Fallback to DashScope

    if provider == "dashscope":
        from services.dashscope_service import DashScopeAIService
        service = DashScopeAIService()
        if service.is_available():
            return service
        else:
            print("[ERROR] DashScope service not available")
            # Try to fall back to Google as last resort
            from services.google_service import GoogleAIService
            service = GoogleAIService()
            if service.is_available():
                print("[INFO] Falling back to Google service")
                return service

    # If we get here, no service is available
    raise ValueError(f"No AI service available. Please check your configuration.")


def get_available_services() -> list:
    """
    Get a list of all available AI services.

    Returns:
        List of available service names
    """
    available = []

    # Check Google
    try:
        from services.google_service import GoogleAIService
        service = GoogleAIService()
        if service.is_available():
            available.append("google")
    except ImportError:
        pass

    # Check ModelScope
    try:
        from services.modelscope_service import ModelScopeAIService
        service = ModelScopeAIService()
        if service.is_available():
            available.append("modelscope")
    except ImportError:
        pass

    # Check DashScope
    try:
        from services.dashscope_service import DashScopeAIService
        service = DashScopeAIService()
        if service.is_available():
            available.append("dashscope")
    except ImportError:
        pass

    return available