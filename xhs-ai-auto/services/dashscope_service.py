"""
DashScope (Alibaba Cloud Model Studio) service implementation.
Provides access to Qwen and Wanxiang models with free tier quotas.
"""

import os
import json
import re
import time
import requests
from typing import Dict, List, Optional
from datetime import datetime
from io import BytesIO
from PIL import Image

from config import settings
from services.ai_service import AIService

try:
    import dashscope
    from dashscope import Generation, ImageSynthesis, MultiModalConversation
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    print("[WARNING] dashscope not installed. Run: pip install dashscope")


class DashScopeAIService(AIService):
    """DashScope/Alibaba Cloud Model Studio service implementation."""

    def __init__(self):
        """Initialize DashScope service with API credentials."""
        self.api_key = settings.DASHSCOPE_API_KEY
        self.text_model = settings.QIANWEN_MODEL_NAME
        self.image_model = settings.WANXIANG_MODEL_NAME

        # Set API key globally for dashscope
        if DASHSCOPE_AVAILABLE and self.api_key:
            dashscope.api_key = self.api_key

    def is_available(self) -> bool:
        """Check if DashScope service is properly configured."""
        if not DASHSCOPE_AVAILABLE:
            print("[ERROR] DashScope SDK not installed")
            return False

        if not self.api_key:
            print("[WARNING] DASHSCOPE_API_KEY is not configured")
            return False

        return True

    def generate_text_content(self, prompt: str) -> Dict:
        """
        Generate text content using Tongyi Qianwen model.

        Args:
            prompt: Topic for content generation

        Returns:
            Dict with title, content, and tags
        """
        if not self.is_available():
            return {}

        try:
            print(f"[INFO] Using DashScope model: {self.text_model}")

            # System prompt for Xiaohongshu content
            system_message = """你是一个专业的小红书内容创作助手。
你需要根据用户提供的主题，生成符合小红书风格的内容。
输出必须是一个有效的JSON对象，格式如下：
{
  "title": "吸引眼球的标题（最多20字）",
  "content": "详细内容（300-500字，包含emoji，实用性强）",
  "tags": ["标签1", "标签2", "标签3"]
}

要求：
1. 标题要吸引人，使用数字、emoji等元素
2. 内容要分段，使用emoji装饰，提供实用价值
3. 标签要精准，3-5个相关标签"""

            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"请为以下主题创作小红书内容：{prompt}"}
            ]

            # Call Qianwen API
            response = Generation.call(
                model=self.text_model,
                messages=messages,
                result_format='message',
                temperature=0.7,
                max_tokens=2000
            )

            if response.status_code == 200:
                content = response.output.choices[0].message.content
                print(f"[DEBUG] Generated content: {content[:200]}...")
                return self._parse_json_response(content)
            else:
                print(f"[ERROR] Text generation failed: {response.code} - {response.message}")
                return {}

        except Exception as e:
            print(f"[ERROR] DashScope text generation error: {e}")
            return {}

    def generate_images(self, text_content: str, save_dir: str, num_images: int = 1) -> List[str]:
        """
        Generate images using Tongyi Wanxiang or Qwen-Image model.

        Args:
            text_content: Text description for image generation
            save_dir: Directory to save images
            num_images: Number of images to generate

        Returns:
            List of saved image paths
        """
        if not self.is_available():
            return []

        try:
            print(f"[INFO] Generating images with model: {self.image_model}")

            # Generate optimized image prompt
            image_prompt = self._generate_image_prompt(text_content)
            print(f"[INFO] Image prompt: {image_prompt[:100]}...")

            saved_paths = []

            # Check which model to use
            if self.image_model == "qwen-image":
                # Use new Qwen-Image model
                saved_paths = self._generate_with_qwen_image(image_prompt, save_dir, num_images)
            else:
                # Use traditional Wanxiang model
                saved_paths = self._generate_with_wanxiang(image_prompt, save_dir, num_images)

            return saved_paths

        except Exception as e:
            print(f"[ERROR] DashScope image generation error: {e}")
            return []

    def _generate_with_qwen_image(self, prompt: str, save_dir: str, num_images: int) -> List[str]:
        """Generate images using Qwen-Image model."""
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"text": prompt}
                    ]
                }
            ]

            # Call Qwen-Image API
            response = MultiModalConversation.call(
                model="qwen-image",
                messages=messages,
                result_format='message',
                stream=False,
                watermark=True,
                prompt_extend=True,
                size='1024*1024'
            )

            if response.status_code == 200:
                # Extract image URLs from response
                saved_paths = []

                # Parse response to get image URLs
                if hasattr(response.output.choices[0].message, 'content'):
                    content = response.output.choices[0].message.content

                    # Look for image URLs in content
                    if isinstance(content, list):
                        for item in content:
                            if 'image' in item:
                                url = item['image']
                                path = self._download_and_save_image(url, save_dir, len(saved_paths))
                                if path:
                                    saved_paths.append(path)
                    elif isinstance(content, str):
                        # Extract URLs from string
                        import re
                        urls = re.findall(r'https?://[^\s]+', content)
                        for i, url in enumerate(urls[:num_images]):
                            path = self._download_and_save_image(url, save_dir, i)
                            if path:
                                saved_paths.append(path)

                print(f"[INFO] Generated {len(saved_paths)} images with Qwen-Image")
                return saved_paths
            else:
                print(f"[ERROR] Qwen-Image failed: {response.code} - {response.message}")
                return []

        except Exception as e:
            print(f"[ERROR] Qwen-Image generation error: {e}")
            return []

    def _generate_with_wanxiang(self, prompt: str, save_dir: str, num_images: int) -> List[str]:
        """Generate images using Tongyi Wanxiang model."""
        try:
            # Call Wanxiang API (synchronous)
            response = ImageSynthesis.call(
                model=ImageSynthesis.Models.wanx_v1,
                prompt=prompt,
                n=num_images,
                size='1024*1024',
                style='<auto>'
            )

            if response.status_code == 200:
                saved_paths = []

                # Save images from response
                for i, result in enumerate(response.output.results):
                    if hasattr(result, 'url'):
                        path = self._download_and_save_image(result.url, save_dir, i)
                        if path:
                            saved_paths.append(path)

                print(f"[INFO] Generated {len(saved_paths)} images with Wanxiang")
                return saved_paths
            else:
                print(f"[ERROR] Wanxiang failed: {response.code} - {response.message}")

                # Try async mode as fallback
                return self._generate_with_wanxiang_async(prompt, save_dir, num_images)

        except Exception as e:
            print(f"[ERROR] Wanxiang generation error: {e}")
            return []

    def _generate_with_wanxiang_async(self, prompt: str, save_dir: str, num_images: int) -> List[str]:
        """Generate images using Wanxiang async mode."""
        try:
            print("[INFO] Using async mode for Wanxiang")

            # Submit async task
            response = ImageSynthesis.async_call(
                model=ImageSynthesis.Models.wanx_v1,
                prompt=prompt,
                n=num_images,
                size='1024*1024'
            )

            if response.status_code == 200:
                task_id = response.output.task_id
                print(f"[INFO] Task submitted: {task_id}")

                # Poll for results
                max_attempts = 30
                for attempt in range(max_attempts):
                    time.sleep(2)  # Wait 2 seconds between polls

                    status_response = ImageSynthesis.fetch(task_id)

                    if status_response.status_code == 200:
                        if status_response.output.task_status == 'SUCCEEDED':
                            # Save images
                            saved_paths = []
                            for i, result in enumerate(status_response.output.results):
                                if hasattr(result, 'url'):
                                    path = self._download_and_save_image(result.url, save_dir, i)
                                    if path:
                                        saved_paths.append(path)

                            print(f"[SUCCESS] Async generation completed")
                            return saved_paths
                        elif status_response.output.task_status == 'FAILED':
                            print("[ERROR] Task failed")
                            return []

                    print(f"[INFO] Polling attempt {attempt+1}/{max_attempts}...")

                print("[ERROR] Timeout waiting for async task")
                return []
            else:
                print(f"[ERROR] Async task submission failed: {response.code}")
                return []

        except Exception as e:
            print(f"[ERROR] Wanxiang async error: {e}")
            return []

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

            # Fallback: create content from response
            return self._create_fallback_content(response_text)

        except json.JSONDecodeError:
            return self._create_fallback_content(response_text)

    def _create_fallback_content(self, text: str) -> Dict:
        """Create fallback content when JSON parsing fails."""
        lines = text.strip().split('\n')
        title = lines[0][:20] if lines else "小红书笔记"
        content = '\n'.join(lines[1:]) if len(lines) > 1 else text

        return {
            'title': title,
            'content': content[:500],
            'tags': ["分享", "日常", "生活"]
        }

    def _generate_image_prompt(self, text_content: str) -> str:
        """Generate optimized prompt for image generation."""
        # Create a concise, descriptive prompt
        if len(text_content) > 200:
            text_content = text_content[:200]

        # Add style guidance for social media
        prompt = f"高质量社交媒体配图，主题：{text_content}。风格：现代、清新、明亮、专业摄影"

        return prompt

    def _download_and_save_image(self, img_url: str, save_dir: str, index: int) -> Optional[str]:
        """Download and save image from URL."""
        try:
            print(f"[INFO] Downloading image from: {img_url[:50]}...")

            response = requests.get(img_url, timeout=30)
            if response.status_code == 200:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(save_dir, f"dashscope_image_{timestamp}_{index+1}.png")

                img = Image.open(BytesIO(response.content))
                img.save(filename)

                print(f"[SUCCESS] Image saved to: {filename}")
                return os.path.abspath(filename)
            else:
                print(f"[ERROR] Failed to download image: {response.status_code}")
                return None

        except Exception as e:
            print(f"[ERROR] Error downloading image {index+1}: {e}")
            return None