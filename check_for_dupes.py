import json
import os
from datetime import datetime, timedelta

js_file = './data/news_articles.js'
images_dir = './ai_generated'

def extract_json_from_js(js_filepath):
    """Extract JSON content from a JS file starting with 'export default'."""
    with open(js_filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    if content.startswith('export default '):
        content = content[len('export default '):].strip(' ;')
    return json.loads(content)

def list_images_in_directory(directory):
    """List all image files in the specified directory."""
    return {file for file in os.listdir(directory) if file.endswith(('.png', '.jpg', '.jpeg'))}

def normalize_item(item):
    """Create a normalized identifier for a news item."""
    normalized_title = item['title'].strip().lower()
    sentiment_score = str(item['sentiment_score']).strip()
    return normalized_title + sentiment_score

def find_unreferenced_images(js_data, image_directory):
    """Find images in the directory that are not referenced in the JSON data."""
    image_urls = set(item.get('image_url') for item in js_data if item.get('image_url'))
    image_filenames = set(url.split('/')[-1] for url in image_urls if 'ai_generated' in url)
    directory_images = list_images_in_directory(image_directory)
    return directory_images - image_filenames

# Main execution
try:
    # Load JSON data from JS file
    js_data = extract_json_from_js(js_file)

    # Current time minus 24 hours
    cutoff_date = datetime.now() - timedelta(days=4)

    # Track seen items and filter duplicates
    seen = set()
    new_data = []
    for item in js_data:
        identifier = normalize_item(item)
        if identifier not in seen and datetime.strptime(item['date'], '%Y-%m-%d %H:%M:%S') > cutoff_date:
            new_data.append(item)
            seen.add(identifier)

    # Write back to file
    cleaned_json = json.dumps(new_data, indent=4, ensure_ascii=False)
    with open(js_file, 'w', encoding='utf-8') as file:
        file.write(f'export default {cleaned_json};')
    print("Old news and duplicates removed and file updated successfully!")

    # Find and delete unreferenced images
    unreferenced_images = find_unreferenced_images(new_data, images_dir)
    if unreferenced_images:
        for image in unreferenced_images:
            os.remove(os.path.join(images_dir, image))
            print(f"Deleted: {image}")
    else:
        print("No unreferenced images found.")

except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

print("Deprecated AI images removed successfully!")
