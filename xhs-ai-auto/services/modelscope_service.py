"""
ModelScope API-Inference service implementation.
Provides 2000 free API calls per day for text and image generation.
"""

import os
import json
import re
import requests
import time
from typing import Dict, List, Optional
from datetime import datetime
from io import BytesIO
from PIL import Image
from openai import OpenAI

from config import settings
from services.ai_service import AIService


class ModelScopeAIService(AIService):
    """ModelScope API-Inference service implementation."""

    def __init__(self):
        """Initialize ModelScope service with API credentials."""
        self.api_key = settings.MODELSCOPE_API_KEY
        self.text_model = settings.MS_TEXT_MODEL
        self.image_model = settings.MS_IMAGE_MODEL
        self.enable_thinking = settings.MS_ENABLE_THINKING

        # Initialize OpenAI-compatible client for text generation
        if self.api_key:
            self.client = OpenAI(
                base_url='https://api-inference.modelscope.cn/v1/',
                api_key=self.api_key,
            )
            print(f"[DEBUG] ModelScope API Key configured: {self.api_key[:10]}...")
        else:
            self.client = None
            print("[WARNING] ModelScope API Key not found")

    def is_available(self) -> bool:
        """Check if ModelScope service is properly configured."""
        if not self.api_key:
            print("[WARNING] MODELSCOPE_API_KEY is not configured")
            return False

        # Try a simple API call to verify connectivity
        try:
            if self.client:
                # Test with a minimal request
                response = self.client.models.list()
                return True
        except Exception as e:
            print(f"[WARNING] ModelScope API test failed: {e}")
            return False

        return True

    def generate_text_content(self, prompt: str) -> Dict:
        """
        Generate text content using Qwen model via ModelScope API-Inference.

        Args:
            prompt: Topic for content generation

        Returns:
            Dict with title, content, and tags
        """
        if not self.client:
            print("[ERROR] ModelScope client not initialized")
            return {}

        try:
            print(f"[INFO] Using ModelScope model: {self.text_model}")
            print(f"[INFO] Thinking mode enabled: {self.enable_thinking}")

            # System prompt for Xiaohongshu content
            system_prompt = """你是一个专业的小红书内容创作助手。
你需要根据用户提供的主题，生成符合小红书风格的内容。
输出必须是一个有效的JSON对象，包含以下三个键：
1. "title": 标题（最多20个字，吸引眼球）
2. "content": 正文内容（300-500字，包含emoji，分段清晰，实用性强）
3. "tags": 标签列表（3-5个相关标签）

示例输出：
{
  "title": "周末宅家也能瘦！懒人减脂秘籍✨",
  "content": "姐妹们！谁说减肥一定要去健身房？今天分享我的懒人减脂法～\n\n🌟 早餐这样吃\n...",
  "tags": ["减脂", "懒人瘦身", "宅家运动", "健康生活"]
}"""

            # Call API with thinking mode support
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"请为以下主题创作小红书内容：{prompt}"}
            ]

            # Add thinking configuration if enabled
            extra_body = {}
            if self.enable_thinking and 'thinking' in self.text_model.lower():
                extra_body = {
                    'enable_thinking': True,
                    'thinking_budget': 8192
                }

            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                stream=False,
                **({'extra_body': extra_body} if extra_body else {})
            )

            # Extract and parse response
            content = response.choices[0].message.content
            print(f"[DEBUG] Raw response: {content[:200]}...")

            return self._parse_json_response(content)

        except Exception as e:
            print(f"[ERROR] ModelScope text generation failed: {e}")
            return {}

    def generate_images(self, text_content: str, save_dir: str, num_images: int = 1) -> List[str]:
        """
        Generate images using ModelScope API-Inference with async mode.
        Supports FLUX, Stable Diffusion, and other AIGC models.

        Args:
            text_content: Text description for image generation
            save_dir: Directory to save images
            num_images: Number of images to generate

        Returns:
            List of saved image paths
        """
        if not self.api_key:
            print("[ERROR] ModelScope API key not configured")
            return []

        try:
            print(f"[INFO] Generating images with model: {self.image_model}")

            # Generate optimized image prompt
            image_prompt = self._generate_image_prompt(text_content)
            print(f"[INFO] Image prompt: {image_prompt[:100]}...")

            model_to_use = self.image_model
            if "qwen-image" in model_to_use.lower():
                print("[INFO] Correcting model name to 'Qwen/Qwen-Image' for API call")
                model_to_use = "Qwen/Qwen-Image"

            base_url = 'https://api-inference.modelscope.cn/'
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-ModelScope-Async-Mode": "true"  # Enable async mode
            }

            # Step 1: Submit image generation task
            print(f"[INFO] Submitting image generation task with model: {model_to_use}")

            payload = {
                "model": model_to_use,
                "prompt": image_prompt
            }

            response = requests.post(
                f"{base_url}v1/images/generations",
                headers=headers,
                data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                timeout=30
            )

            if response.status_code != 200:
                print(f"[ERROR] Failed to submit task: {response.status_code}")
                print(f"[ERROR] Response: {response.text[:500]}")
                return []

            task_id = response.json().get("task_id")
            if not task_id:
                print("[ERROR] No task_id returned from API")
                return []

            print(f"[INFO] Task submitted successfully, task_id: {task_id}")

            # Step 2: Poll for task completion
            max_attempts = 60  # Wait up to 2 minutes
            poll_interval = 2  # Check every 2 seconds

            for attempt in range(max_attempts):
                time.sleep(poll_interval)

                result_response = requests.get(
                    f"{base_url}v1/tasks/{task_id}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "X-ModelScope-Task-Type": "image_generation"
                    },
                    timeout=10
                )

                if result_response.status_code != 200:
                    print(f"[WARNING] Failed to check task status: {result_response.status_code}")
                    continue

                data = result_response.json()
                task_status = data.get("task_status")

                print(f"[INFO] Task status: {task_status} (attempt {attempt + 1}/{max_attempts})")

                if task_status == "SUCCEED":
                    # Download and save images
                    output_images = data.get("output_images", [])
                    if not output_images:
                        print("[ERROR] No images in response")
                        return []

                    saved_paths = []
                    for i, img_url in enumerate(output_images[:num_images]):
                        print(f"[INFO] Downloading image {i+1} from: {img_url[:50]}...")

                        try:
                            img_response = requests.get(img_url, timeout=30)
                            if img_response.status_code == 200:
                                img = Image.open(BytesIO(img_response.content))

                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = os.path.join(save_dir, f"modelscope_image_{timestamp}_{i+1}.png")
                                img.save(filename)

                                saved_paths.append(os.path.abspath(filename))
                                print(f"[SUCCESS] Image saved to: {filename}")
                            else:
                                print(f"[ERROR] Failed to download image: {img_response.status_code}")
                        except Exception as e:
                            print(f"[ERROR] Error downloading image {i+1}: {e}")

                    if saved_paths:
                        return saved_paths
                    else:
                        return []

                elif task_status == "FAILED":
                    error_msg = data.get("error", "Unknown error")
                    print(f"[ERROR] Task failed: {error_msg}")
                    return []

                elif task_status not in ["PENDING", "RUNNING"]:
                    print(f"[WARNING] Unknown task status: {task_status}")

            print("[ERROR] Timeout waiting for image generation")
            return self._fallback_to_placeholder(image_prompt, save_dir, num_images)

        except Exception as e:
            print(f"[ERROR] ModelScope image generation error: {e}")
            return self._fallback_to_placeholder(image_prompt, save_dir, num_images)


    def _save_base64_image(self, b64_data: str, save_dir: str, index: int) -> Optional[str]:
        """Save base64 encoded image."""
        try:
            import base64

            img_bytes = base64.b64decode(b64_data)
            img = Image.open(BytesIO(img_bytes))

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(save_dir, f"modelscope_image_{timestamp}_{index+1}.png")
            img.save(filename)

            print(f"[SUCCESS] Image saved to: {filename}")
            return os.path.abspath(filename)

        except Exception as e:
            print(f"[ERROR] Failed to save base64 image: {e}")
            return None

    def _parse_json_response(self, response_text: str) -> Dict:
        """Parse JSON from model response."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                content = json.loads(json_match.group(0))

                # Validate required fields
                if all(k in content for k in ['title', 'content', 'tags']):
                    # Ensure title is within limit
                    content['title'] = content['title'][:20]
                    return content
                else:
                    print("[WARNING] Response missing required fields")
                    return self._create_fallback_content(response_text)
            else:
                print("[WARNING] No JSON found in response")
                return self._create_fallback_content(response_text)

        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse JSON: {e}")
            return self._create_fallback_content(response_text)

    def _create_fallback_content(self, text: str) -> Dict:
        """Create fallback content when JSON parsing fails."""
        # Extract first line as title
        lines = text.strip().split('\n')
        title = lines[0][:20] if lines else "小红书笔记"

        # Use remaining text as content
        content = '\n'.join(lines[1:]) if len(lines) > 1 else text

        # Generate basic tags
        tags = ["生活分享", "日常"]

        return {
            'title': title,
            'content': content[:500],
            'tags': tags
        }

    def _generate_image_prompt(self, text_content: str) -> str:
        """Generate optimized prompt for image generation."""
        # Extract key elements from content
        prompt = f"Create a beautiful, high-quality image for social media post about: {text_content[:200]}"

        # Add style guidance
        prompt += " Style: modern, clean, vibrant colors, professional photography, trending on social media"

        return prompt

    def _save_image(self, img_data, save_dir: str, index: int) -> Optional[str]:
        """Save image data to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(save_dir, f"modelscope_image_{timestamp}_{index+1}.png")

            # Handle different image data formats
            if isinstance(img_data, str):
                # Base64 encoded image
                import base64
                img_bytes = base64.b64decode(img_data)
                img = Image.open(BytesIO(img_bytes))
            elif isinstance(img_data, bytes):
                # Raw bytes
                img = Image.open(BytesIO(img_data))
            else:
                # Already a PIL Image
                img = img_data

            img.save(filename)
            print(f"[SUCCESS] Image saved to: {filename}")
            return os.path.abspath(filename)

        except Exception as e:
            print(f"[ERROR] Failed to save image {index+1}: {e}")
            return None

    def _download_and_save_image(self, img_url: str, save_dir: str, index: int) -> Optional[str]:
        """Download and save image from URL."""
        try:
            response = requests.get(img_url, timeout=30)
            if response.status_code == 200:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(save_dir, f"modelscope_image_{timestamp}_{index+1}.png")

                img = Image.open(BytesIO(response.content))
                img.save(filename)

                print(f"[SUCCESS] Image downloaded and saved to: {filename}")
                return os.path.abspath(filename)
            else:
                print(f"[ERROR] Failed to download image from {img_url}")
                return None

        except Exception as e:
            print(f"[ERROR] Error downloading image {index+1}: {e}")
            return None