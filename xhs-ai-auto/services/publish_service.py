import requests
import json
from config import settings

def publish_note(title: str, content: str, tags: list, local_image_paths: list[str]) -> bool:
    """
    Publishes a note to Xiaohongshu by calling the xiaohongshu-mcp service using MCP protocol.

    Args:
        title: The title of the note.
        content: The main body of the note.
        tags: A list of tags for the note.
        local_image_paths: A list of absolute local file paths for the images.

    Returns:
        True if publishing was successful, False otherwise.
    """
    mcp_url = f"{settings.XHS_MCP_BASE_URL}/mcp"  # Use /mcp endpoint for MCP protocol

    if not local_image_paths:
        print("Error: No local image paths provided. Aborting publish.")
        return False

    # Construct the MCP request
    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "publish_content",
            "arguments": {
                "title": title[:20],  # Xiaohongshu title limit is 20 characters
                "content": content,
                "images": local_image_paths  # Changed from image_paths to images
            }
        },
        "id": 1
    }

    headers = {"Content-Type": "application/json"}

    try:
        print("\nSending MCP request to xiaohongshu-mcp service...")
        print(f"Title: {title[:20]}")
        print(f"Content length: {len(content)} characters")
        print(f"Images: {len(local_image_paths)} files")

        response = requests.post(mcp_url, headers=headers, json=mcp_request, timeout=180)
        response.raise_for_status()
        response_data = response.json()

        # Check MCP response
        if "error" in response_data:
            error = response_data["error"]
            print(f"MCP Error: {error.get('message', 'Unknown error')}")
            if "data" in error:
                print(f"Error details: {error['data']}")
            return False

        if "result" in response_data:
            result = response_data["result"]
            print(f"[DEBUG] MCP Result: {result}")

            # Check if the result indicates success
            if isinstance(result, dict):
                # Check for various success indicators
                if (result.get("success") or
                    "成功" in str(result.get("message", "")) or
                    result.get("status") == "success" or
                    # If there's no error field and no failure indicators, assume success
                    (not result.get("error") and not result.get("failed"))):
                    print("Successfully published note to Xiaohongshu!")
                    if "message" in result:
                        print(f"Response: {result['message']}")
                    return True
                else:
                    print(f"Failed to publish: {result.get('message', result.get('error', 'Unknown error'))}")
                    return False
            elif isinstance(result, list):
                # If result is a list, check if it contains success info
                print(f"MCP Response (list): {result}")
                # For list responses, assume success if not empty
                return len(result) > 0
            else:
                # For other formats (string, etc), assume success if no error indicators
                result_str = str(result).lower()
                if "error" in result_str or "failed" in result_str:
                    print(f"Failed to publish: {result}")
                    return False
                print(f"MCP Response: {result}")
                return True  # Assume success if no error indicators
        else:
            print(f"Unexpected MCP response format: {response_data}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Error calling xiaohongshu-mcp service: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text[:500]}")  # Print first 500 chars
        return False
    except Exception as e:
        print(f"An unexpected error occurred during publishing: {e}")
        return False

if __name__ == '__main__':
    # This block is for direct testing of this module.
    # NOTE: To run this test, you need a pre-existing image file.
    # The main.py workflow is the intended way to use the full system.
    import os

    print("--- Testing Publish Service ---")
    # This requires the xiaohongshu-mcp service to be running.

    # Create a dummy image file for testing purposes
    dummy_image_path = "dummy_test_image.png"
    if not os.path.exists(dummy_image_path):
        try:
            from PIL import Image
            img = Image.new('RGB', (100, 100), color = 'red')
            img.save(dummy_image_path)
            print(f"Created a dummy image for testing: {dummy_image_path}")
        except ImportError:
            print("Pillow is not installed. Cannot create a dummy image for testing.")
            dummy_image_path = ""

    if dummy_image_path:
        test_title = "Local Publish Test"
        test_content = "This is a test post using a local image file. 🛠️"
        test_tags = ["testing", "local", "development"]
        test_image_paths = [os.path.abspath(dummy_image_path)]

        success = publish_note(test_title, test_content, test_tags, test_image_paths)

        if success:
            print("\\nTest finished: PUBLISH SUCCESSFUL")
        else:
            print("\\nTest finished: PUBLISH FAILED")

        # Clean up the dummy image
        os.remove(dummy_image_path)
    else:
        print("Skipping publish test because no dummy image could be created.")
