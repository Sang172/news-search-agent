# Simple Reflex AI Agent for News Search

## Overview
This is a simple Flask-based web application that enables users to search for recent (within the last 2 days specifially) news articles using a simple reflex AI agent. The AI classifies user queries into different search types and fetches relevant news from major U.S. news outlets. The classification process is powered by Anthropic's Claude AI via AWS Bedrock, and news retrieval is handled using the `gnews` Python package.

## Features
- **Automated News Classification**: The AI classifies user queries as "keyphrase", "topic", or "general" search.
- **Keyphrase Search**: Extracts key phrases from user input and retrieves relevant articles.
- **Topic-Based Search**: Searches for news within predefined topics such as politics, business, sports, entertainment, technology, and international affairs.
- **General News Search**: Returns top trending news articles.
- **AWS Bedrock Integration**: Uses Anthropic's Claude model for natural language processing.
- **Flask Web Interface**: A simple web UI for submitting news search queries.

## Usage
1. Enter a search query into the web interface.
2. The AI will classify the search intent as:
   - **Keyphrase search**: If specific phrases are detected.
   - **Topic search**: If the query matches predefined topics.
   - **General search**: If no specific topic or keyphrase is found.
3. The system fetches relevant news articles and displays them in the UI.
   
## Deployment
The project is containerized using Docker and deployed to AWS App Runner. A Continuous Integration and Continuous Deployment (CI/CD) pipeline using GitHub Actions automates the build, test, and deployment process.

## Links
- [Demo Video](https://youtu.be/vo1jN7eYtsI)