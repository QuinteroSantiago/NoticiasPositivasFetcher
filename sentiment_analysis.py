from transformers import AutoTokenizer, AutoModelForSequenceClassification, file_utils
import torch
import requests

# Extend default timeout
file_utils.DEFAULT_TIMEOUT = (10, 100)

# Load the pre-trained BERT model and tokenizer
try:
    tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-xlm-roberta-base-sentiment")
    model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-xlm-roberta-base-sentiment")
except requests.exceptions.ReadTimeout as e:
    print(f"Failed to load model due to timeout: {e}")
    # Additional logic to handle the failure (e.g., retry, fallback to local model, etc.)

# Function to perform sentiment analysis on input text
def sentiment_analysis(text):
    try:
        # Tokenize input text
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)

        # Get model predictions
        outputs = model(**inputs)

        # Calculate sentiment score
        sentiment_score = outputs.logits.softmax(dim=-1)
        sentiment_score = sentiment_score[:, 2].item() - sentiment_score[:, 0].item()  # Positive score - Negative score

        return sentiment_score
    except Exception as e:
        print(f"An error occurred during sentiment analysis: {e}")
        return 0  # or handle the error in a way that fits your application context

