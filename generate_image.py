import base64
import os
import requests
import uuid
from deep_translator import GoogleTranslator

# Stability AI API configuration
engine_id = "stable-diffusion-v1-6"
api_host = os.getenv('API_HOST', 'https://api.stability.ai')
api_key = os.getenv("STABILITY_API_KEY")

if api_key is None:
    raise Exception("Missing Stability API key.")

def generate_image(prompt):
    prompt = GoogleTranslator(source='auto', target='en').translate(prompt)
    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "text_prompts": [
                {
                    "text": prompt
                }
            ],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30,
        },
    )

    if response.status_code != 200:
        print("(generate-image) Non-200 response: " + str(response.text))
        return '/assets/placeholder-for-na.png'


    data = response.json()

    output_dir = './ai_generated'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_path = None
    for i, image in enumerate(data["artifacts"]):
        random_string = uuid.uuid4().hex
        image_path = f"{output_dir}/v1_txt2img_{random_string}.png"
        image_path_public = f"./ai_generated/v1_txt2img_{random_string}.png"
        with open(image_path_public, "wb") as f:
            f.write(base64.b64decode(image["base64"]))

    return image_path
