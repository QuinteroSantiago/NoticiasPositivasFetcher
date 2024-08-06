#!/bin/bash

# Create the dist directory if it doesn't exist
mkdir -p dist

# Create required subdirectories
mkdir -p dist/public/assets/ai_generated
mkdir -p dist/data

# Copy the contents of ai_generated to the new directory
cp -r ai_generated/* dist/public/assets/ai_generated/

# Copy news_articles.json to the data directory
cp news_articles.json dist/data/
