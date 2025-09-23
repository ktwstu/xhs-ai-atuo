import os
from google_ai import GoogleTextGenerator, GoogleImageGenerator, build_image_prompt


def main():
    topic = os.environ.get("TEST_TOPIC", "一个健康早餐的创意分享")
    out_dir = os.environ.get("TEST_OUT_DIR", os.path.join("data", "google_ai_test"))
    n = int(os.environ.get("TEST_NUM_IMAGES", "1"))

    print("[TEST] Generating text with GoogleTextGenerator...")
    tg = GoogleTextGenerator()
    text_result = tg.generate(topic)
    print("[TEST] Text result:", text_result)

    if not text_result:
        print("[TEST] No text result, aborting image generation.")
        return

    prompt = text_result.get("image_prompt") or build_image_prompt(text_result.get("content", topic))

    print("[TEST] Generating images with GoogleImageGenerator...")
    ig = GoogleImageGenerator()
    paths = ig.generate(text_result.get("content", topic), out_dir=out_dir, n=n, image_prompt=prompt)
    print("[TEST] Saved images:", paths)


if __name__ == "__main__":
    main()
