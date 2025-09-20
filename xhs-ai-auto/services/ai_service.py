"""
Abstract interface for AI services.
This module defines the base interface that all AI service implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class AIService(ABC):
    """Abstract base class for AI service implementations."""

    @abstractmethod
    def generate_text_content(self, prompt: str) -> Dict:
        """
        Generate text content for a Xiaohongshu note.

        Args:
            prompt: The topic or prompt for content generation

        Returns:
            Dict containing:
                - title: The note title (max 20 characters)
                - content: The main content
                - tags: List of relevant tags
                - image_prompt: (Optional) Optimized prompt for image generation
        """
        pass

    @abstractmethod
    def generate_images(self, text_content: str, save_dir: str, num_images: int = 1, image_prompt: Optional[str] = None) -> List[str]:
        """
        Generate images based on text content.

        Args:
            text_content: Text description for image generation
            save_dir: Directory to save generated images
            num_images: Number of images to generate (default: 1)
            image_prompt: (Optional) Specific prompt for image generation

        Returns:
            List of absolute paths to saved images
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the service is available and properly configured.

        Returns:
            True if service is available, False otherwise
        """
        pass

    def get_service_name(self) -> str:
        """
        Get the name of the AI service provider.

        Returns:
            Service provider name
        """
        return self.__class__.__name__.replace('AIService', '')