from google import genai
from google.genai import types
from PIL import Image
import json
import re
import os
from datetime import datetime
from config import settings
from io import BytesIO

def generate_text_content(prompt: str) -> dict:
    """
    Generates text content for a Xiaohongshu note using the Google Gemini API.
    This function now uses the correct genai.Client method.
    """
    if not settings.GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY is not configured in the .env file.")
        return {}
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
    except Exception as e:
        print(f"Error initializing Gemini Client: {e}")
        return {}

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

    try:
        print(f"Sending prompt to Gemini model: {settings.GEMINI_MODEL_NAME}...")
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL_NAME,
            contents=full_prompt
        )
        cleaned_response_text = re.search(r'\{[\s\S]*\}', response.text)
        if not cleaned_response_text:
            print("Error: Could not find a valid JSON object in the model's response.")
            print("Raw Gemini Response:", response.text)
            return {}

        content = json.loads(cleaned_response_text.group(0))

        if all(k in content for k in ['title', 'content', 'tags']):
            return content
        else:
            print("Error: Gemini response is missing required keys.")
            print("Received JSON:", content)
            return {}
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        if 'response' in locals():
            print("Raw Gemini Response:", response.text)
        return {}

def _generate_image_prompt_with_gemini(text_content: str) -> str:
    """
    Uses Gemini to generate a highly descriptive, artistic English prompt for an image generation model.
    """
    if not settings.GEMINI_API_KEY:
        return f"A beautiful social media image about: {text_content[:100]}"
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        full_prompt = f"You are an expert in visual art. Based on the text, create a concise, highly descriptive, and artistic prompt in English for an AI image model like Imagen. Focus on visual details, style, and lighting. The prompt should be a single, fluent sentence. Text: \"{text_content[:300]}\""
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=full_prompt
        )
        return response.text.strip()
    except Exception:
        return f"A beautiful social media image about: {text_content[:100]}"

def generate_images(text_content: str, save_dir: str, num_images: int = 1) -> list[str]:
    """
    Generates images using Google's Imagen model and saves them to a local directory.
    This function now uses the correct BytesIO method as per the official documentation.
    """
    print(f"\n[INFO] Starting image generation process...")
    print(f"[INFO] Save directory: {save_dir}")
    print(f"[INFO] Number of images requested: {num_images}")

    if not settings.IMAGEN_API_KEY:
        print("[ERROR] IMAGEN_API_KEY is not configured. Cannot generate images.")
        return []

    try:
        print(f"[INFO] Initializing Imagen Client...")
        client = genai.Client(api_key=settings.IMAGEN_API_KEY)
        print(f"[INFO] Imagen Client initialized successfully")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Imagen Client: {e}")
        print(f"[ERROR] Exception type: {type(e).__name__}")
        return []

    print("\n[INFO] Generating an optimized image prompt with Gemini...")
    image_prompt = _generate_image_prompt_with_gemini(text_content)
    print(f"[INFO] Optimized Image Prompt: {image_prompt}")

    try:
        print(f"\n[INFO] Calling Imagen API...")
        print(f"[INFO] Model: {settings.IMAGEN_MODEL_NAME}")
        print(f"[INFO] Prompt length: {len(image_prompt)} characters")

        response = client.models.generate_images(
            model=settings.IMAGEN_MODEL_NAME,
            prompt=image_prompt,
            config=types.GenerateImagesConfig(number_of_images=num_images)
        )

        print(f"[INFO] API call successful, received response")
        print(f"[INFO] Response type: {type(response).__name__}")

        if hasattr(response, 'generated_images'):
            print(f"[INFO] Number of generated images: {len(response.generated_images)}")
        else:
            print(f"[ERROR] Response does not have 'generated_images' attribute")
            print(f"[ERROR] Response attributes: {dir(response)}")
            return []

        saved_image_paths = []
        for i, img_data in enumerate(response.generated_images):
            print(f"\n[INFO] Processing image {i+1}/{len(response.generated_images)}...")

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
                filename = os.path.join(save_dir, f"generated_image_{timestamp}_{i+1}.png")

                print(f"[INFO] Saving image to: {filename}")
                img.save(filename)

                saved_image_paths.append(os.path.abspath(filename))
                print(f"[SUCCESS] Image {i+1} saved successfully")

            except Exception as img_error:
                print(f"[ERROR] Failed to process image {i+1}: {img_error}")
                print(f"[ERROR] Exception type: {type(img_error).__name__}")
                if hasattr(img_data, '__dict__'):
                    print(f"[DEBUG] img_data attributes: {img_data.__dict__.keys()}")
                continue

        print(f"\n[SUCCESS] Total images saved: {len(saved_image_paths)}")
        return saved_image_paths

    except Exception as e:
        print(f"\n[ERROR] Image generation failed: {e}")
        print(f"[ERROR] Exception type: {type(e).__name__}")

        # Try to extract more error information
        if hasattr(e, '__dict__'):
            print(f"[DEBUG] Error attributes: {e.__dict__}")
        if hasattr(e, 'message'):
            print(f"[ERROR] Error message: {e.message}")
        if hasattr(e, 'code'):
            print(f"[ERROR] Error code: {e.code}")
        if hasattr(e, 'details'):
            print(f"[ERROR] Error details: {e.details}")

        return []

if __name__ == '__main__':
    test_prompt = "A robot artist painting a futuristic cityscape"
    temp_dir = os.path.join("data", "temp_test")
    os.makedirs(temp_dir, exist_ok=True)
    print("--- Testing Gemini Text Generation ---")
    generated_text = generate_text_content(test_prompt)
    if generated_text:
        print(f"Title: {generated_text.get('title')}")
        print(f"Content: {generated_text.get('content')}")
        print(f"Tags: {generated_text.get('tags')}")
        print("\\n--- Testing Google Image Generation ---")
        local_paths = generate_images(generated_text.get('content', ''), save_dir=temp_dir, num_images=1)
        if local_paths:
            print("Generated images saved at:", local_paths)
        else:
            print("Image generation failed.")
    else:
        print("Text generation failed.")
