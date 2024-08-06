import requests
import pandas as pd
from sentiment_analysis import sentiment_analysis
from generate_image import generate_image
import os

import json

def news_fetcher():
    api_key = os.getenv("NEWS_DATA_API_KEY")
    if api_key is None:
        raise Exception("Missing News Data IO API key.")

    sources = ["www.infobae.com/espana/", "cnnespanol.cnn.com", "www.abc.es", "elpais.com/espana", "Real Madrid", "Barcelona"]
    all_articles = []

    # Fetch data from all sources
    for source in sources:
        response = requests.get(f'https://newsdata.io/api/1/news?apikey={api_key}&q={source}&country=es,us,ve&language=es&category=business,health,technology,top,world')
        print(f'Response {source}: {response}')
        if response.status_code == 200:
            all_articles.extend(response.json().get('results', []))
    response = requests.get(f'https://newsdata.io/api/1/news?apikey={api_key}&q=2001online.com&country=ve&language=es&category=top')
    print(f'Response 2001online.com: {response}')
    all_articles.extend(response.json().get('results', []))

    print(f'all_articles: {all_articles}')

    # Convert data to DataFrame
    df = pd.DataFrame(all_articles)

    # Add sentiment score to dataframe
    df['sentiment_score'] = 0.0

    # Traverse DataFrame for sentiment analysis
    for index, row in df.iterrows():
        desc = row['description']
        if pd.isna(desc):
            text = row['title']
        else:
            text = row['description']
        sentiment = sentiment_analysis(text.lower())
        df.at[index, 'sentiment_score'] = float(sentiment)

    return df.to_dict(orient='records')

def create_json_structure(json_array):
    articles_db = {}

    for index, row in enumerate(json_array):
        article_id = index + 1
        keywords = row.get('keywords')
        category = row.get('category')
        if keywords:
            if isinstance(keywords, list):
                tags = keywords
            else:
                tags = list(set(keywords.split(',')))
        elif category:
            tags = category
        else:
            tags = []

        img_url = row.get('image_url')
        if not img_url:
            prompt = f"Create an image for this news article: {row['title']}"
            img_url = generate_image(prompt)

        articles_db[article_id] = {
            "title": row['title'],
            "imgUrl": img_url,
            "tags": tags,
            "link": row['link'],
            "date": row['pubDate'],
            "sentiment_score": row['sentiment_score'],
            "publisher": row.get('source_id', 'Otros')
        }

    return articles_db

def write_to_json_file(articles_db, file_name='./news_articles.json'):
    # Write the updated data back to the file
    with open(file_name, 'w') as f:
        json.dump(articles_db, f)

def unique_ids(data):
    # Fix duplicate keys by generating new unique ids
    fixed_data = {}
    seen_titles = set()
    idx = 1
    for item in data.values():
        # Check if the title has not been seen before
        if item["title"] not in seen_titles:
            fixed_data[str(idx)] = item
            seen_titles.add(item["title"])
            idx += 1
    return fixed_data

def append_json_to_js(json_file, js_file):
    # Read the JSON data
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading {json_file}: {e}")
        json_data = {}  # Set default if file is missing or empty

    # Format the JSON data for the JavaScript array
    new_entries = []
    for entry in json_data.values():
        new_entries.append({
            "title": entry["title"],
            "image_url": entry["imgUrl"],
            "tags": entry["tags"],
            "link": entry["link"],
            "date": entry["date"],
            "sentiment_score": entry["sentiment_score"]
        })

    # Read the existing JavaScript file
    try:
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()
    except FileNotFoundError:
        print(f"{js_file} not found, creating new file.")
        js_content = "const newsData = [];"

    # Find the start and end of the array
    start_index = js_content.find('[')
    end_index = js_content.rfind(']')
    if start_index == -1 or end_index == -1:
        # Handle missing or malformed array structure
        print("No valid array found in the JS file, resetting file structure.")
        start_index, end_index = js_content.find('['), js_content.rfind(']')

    # Get the existing array content
    existing_array_content = js_content[start_index+1:end_index].strip()

    # Convert the new entries to JavaScript objects
    new_entries_js = ',\n'.join([json.dumps(entry, ensure_ascii=False) for entry in new_entries])

    # Create the updated array content
    updated_array_content = existing_array_content + (',\n' if existing_array_content else '') + new_entries_js

    # Replace the old array content with the updated content
    updated_js_content = js_content[:start_index+1] + updated_array_content + js_content[end_index:]

    # Write the updated content back to the JavaScript file
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(updated_js_content)


# Main process
news_array = news_fetcher()
articles_db = create_json_structure(news_array)
write_to_json_file(articles_db)

json_file = './news_articles.json'
js_file = './data/news_articles.js'

append_json_to_js(json_file, js_file)
