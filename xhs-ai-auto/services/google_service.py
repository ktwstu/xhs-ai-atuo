"""
Google AI service implementation (Gemini + Imagen).
Refactored to implement the AIService interface.
"""

from google import genai
from google.genai import types
from PIL import Image
import json
import re
import os
from datetime import datetime
from io import BytesIO
from typing import Dict, List

from config import settings
from services.ai_service import AIService


class GoogleAIService(AIService):
    """Google AI service implementation using Gemini and Imagen."""

    def __init__(self):
        """Initialize Google AI service with API credentials."""
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.imagen_api_key = settings.IMAGEN_API_KEY
        self.gemini_model = settings.GEMINI_MODEL_NAME
        self.imagen_model = settings.IMAGEN_MODEL_NAME

    def is_available(self) -> bool:
        """Check if Google AI service is properly configured."""
        if not self.gemini_api_key:
            print("[WARNING] GEMINI_API_KEY is not configured")
            return False

        if not self.imagen_api_key:
            print("[WARNING] IMAGEN_API_KEY is not configured")
            return False

        return True

    def generate_text_content(self, prompt: str) -> Dict:
        """
        Generate text content using Google Gemini API.

        Args:
            prompt: Topic for content generation

        Returns:
            Dict with title, content, and tags
        """
        if not self.gemini_api_key:
            print("[ERROR] GEMINI_API_KEY is not configured")
            return {}

        try:
            print(f"[INFO] Using Gemini model: {self.gemini_model}")
            client = genai.Client(api_key=self.gemini_api_key)

            full_prompt = f"""
            You are a helpful assistant that strictly follows instructions. Your task is to generate content for a Xiaohongshu note.
            Your output MUST be a single, valid JSON object and nothing else. Do not include any text before or after the JSON object, such as markdown formatting.

            The JSON object must contain exactly these three keys: "title", "content", and "tags".

            Here is an example of the required output format:
            {{
              "title": "Example Title",
              "content": "This is an example note content with emojis ✨.",
              "tags": ["example", "demo"]
            }}

            Now, generate the content for the following topic.

            USER'S TOPIC: "{prompt}"
            """

            response = client.models.generate_content(
                model=self.gemini_model,
                contents=full_prompt
            )

            cleaned_response_text = re.search(r'\{[\s\S]*\}', response.text)
            if not cleaned_response_text:
                print("[ERROR] Could not find valid JSON in response")
                print(f"[DEBUG] Raw response: {response.text[:200]}")
                return {}

            content = json.loads(cleaned_response_text.group(0))

            if all(k in content for k in ['title', 'content', 'tags']):
                # Ensure title is within limit
                content['title'] = content['title'][:20]
                return content
            else:
                print("[ERROR] Response missing required keys")
                return {}

        except Exception as e:
            print(f"[ERROR] Gemini text generation failed: {e}")
            return {}

    def generate_images(self, text_content: str, save_dir: str, num_images: int = 1) -> List[str]:
        """
        Generate images using Google Imagen API.

        Args:
            text_content: Text description for image generation
            save_dir: Directory to save images
            num_images: Number of images to generate

        Returns:
            List of saved image paths
        """
        if not self.imagen_api_key:
            print("[ERROR] IMAGEN_API_KEY is not configured")
            return []

        try:
            print(f"[INFO] Using Imagen model: {self.imagen_model}")
            client = genai.Client(api_key=self.imagen_api_key)

            # Generate optimized image prompt
            image_prompt = self._generate_image_prompt_with_gemini(text_content)
            print(f"[INFO] Optimized image prompt: {image_prompt[:100]}...")

            print(f"[INFO] Generating {num_images} image(s)...")
            response = client.models.generate_images(
                model=self.imagen_model,
                prompt=image_prompt,
                config=types.GenerateImagesConfig(number_of_images=num_images)
            )

            print(f"[INFO] API call successful, processing images...")

            if hasattr(response, 'generated_images'):
                print(f"[INFO] Number of generated images: {len(response.generated_images)}")
            else:
                print(f"[ERROR] Response does not have 'generated_images' attribute")
                return []

            saved_image_paths = []
            for i, img_data in enumerate(response.generated_images):
                print(f"[INFO] Processing image {i+1}/{len(response.generated_images)}...")

                try:
                    # Check the type of img_data.image
                    print(f"[INFO] Image data type: {type(img_data.image).__name__}")

                    # The response.generated_images[i].image might be a PIL Image object directly
                    if isinstance(img_data.image, Image.Image):
                        print(f"[INFO] Image is already a PIL Image object")
                        img = img_data.image
                    elif isinstance(img_data.image, bytes):
                        print(f"[INFO] Image is raw bytes, converting to PIL Image")
                        img = Image.open(BytesIO(img_data.image))
                    else:
                        print(f"[WARNING] Unknown image type, attempting direct usage")
                        img = img_data.image

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = os.path.join(save_dir, f"google_image_{timestamp}_{i+1}.png")

                    print(f"[INFO] Saving image to: {filename}")
                    img.save(filename)

                    saved_image_paths.append(os.path.abspath(filename))
                    print(f"[SUCCESS] Image {i+1} saved successfully")

                except Exception as img_error:
                    print(f"[ERROR] Failed to process image {i+1}: {img_error}")
                    continue

            print(f"[SUCCESS] Total images saved: {len(saved_image_paths)}")
            return saved_image_paths

        except Exception as e:
            print(f"[ERROR] Imagen generation failed: {e}")
            print(f"[ERROR] Exception type: {type(e).__name__}")

            # Try to extract more error information
            if hasattr(e, '__dict__'):
                print(f"[DEBUG] Error attributes: {e.__dict__}")

            return []

    def _generate_image_prompt_with_gemini(self, text_content: str) -> str:
        """Use Gemini to generate an optimized image prompt."""
        if not self.gemini_api_key:
            return f"A beautiful social media image about: {text_content[:100]}"

        try:
            client = genai.Client(api_key=self.gemini_api_key)
            full_prompt = f"""You are an expert in visual art. Based on the text, create a concise, highly descriptive, and artistic prompt in English for an AI image model like Imagen. Focus on visual details, style, and lighting. The prompt should be a single, fluent sentence. Text: "{text_content[:300]}" """

            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=full_prompt
            )

            return response.text.strip()

        except Exception:
            return f"A beautiful social media image about: {text_content[:100]}"