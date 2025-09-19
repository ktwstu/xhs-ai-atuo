import os
import json
from datetime import datetime
from services.llm_service import generate_text_content, generate_images
from services.publish_service import publish_note

def create_storage_folder(base_path: str, topic: str) -> str:
    """
    Creates a unique, timestamped folder for storing the generated content.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sanitized_topic = "".join(c if c.isalnum() else "_" for c in topic)[:50] # Sanitize and truncate topic
    folder_name = f"{timestamp}_{sanitized_topic}"
    full_path = os.path.join(base_path, folder_name)
    os.makedirs(full_path, exist_ok=True)
    print(f"Created storage folder: {full_path}")
    return full_path

def save_content_locally(folder_path: str, content: dict):
    """
    Saves the generated text content to a local JSON file.
    """
    filepath = os.path.join(folder_path, "content.json")
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        print(f"Content successfully saved to: {filepath}")
    except IOError as e:
        print(f"Error saving content locally: {e}")

def main():
    """
    The main workflow for the xhs-ai-auto assistant.
    """
    print("--- Welcome to the XHS AI Auto Assistant ---")

    # 1. Get user input for the note topic
    topic = input("Please enter the topic for your Xiaohongshu note: ")
    if not topic:
        print("Topic cannot be empty. Exiting.")
        return

    # 2. Create a local folder to store and archive all assets for this run
    storage_path = create_storage_folder("data", topic)

    # 3. Generate text content
    print("\\nStep 1: Generating text content...")
    text_content = generate_text_content(topic)
    if not text_content:
        print("Failed to generate text content. Aborting.")
        return
    print("Text content generated successfully.")
    save_content_locally(storage_path, text_content) # Archive the text content

    # 4. Generate images and save them directly to the storage path
    print("\\nStep 2: Generating images...")
    local_image_paths = generate_images(
        text_content=text_content['content'],
        save_dir=storage_path, # Provide the directory to save images
        num_images=1
    )
    if not local_image_paths:
        print("Failed to generate images. Aborting.")
        return
    print("Images generated and saved successfully.")

    # 5. Publish the note using the generated content and local image paths
    print("\\nStep 3: Publishing to Xiaohongshu...")
    success = publish_note(
        title=text_content['title'],
        content=text_content['content'],
        tags=text_content['tags'],
        local_image_paths=local_image_paths # Pass the local paths directly
    )

    if success:
        print("\\n--- Workflow Complete: Note published successfully! ---")
    else:
        print("\\n--- Workflow Failed: Could not publish the note. ---")

if __name__ == '__main__':
    main()
