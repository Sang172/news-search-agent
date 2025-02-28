import time
import os
from dotenv import load_dotenv
from fetch_news import topic_keywords, keyphrase_search, topic_search, general_search 
from pydantic import BaseModel, Field
from typing import List, Dict, Union, Optional, Tuple
from flask import Flask, request, render_template
import boto3
import json
import gnews

load_dotenv()
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION_NAME = os.environ.get("AWS_REGION", "us-west-2")

class NewsSearchRequest(BaseModel):
    search_type: str = Field(description="Type of news search: 'topic', 'keyphrase', or 'general'")
    keyphrases: List[str] = Field(description="List of keyphrases for keyphrase search", default=[])
    topics: List[str] = Field(description="List of topics for topic search", default=[])

class NewsArticle(BaseModel):
    title: str = Field(description="Title of the news article")
    publisher: str = Field(description="Publisher of the article")
    time: str = Field(description="Publication date of the article")
    url: str = Field(description="URL of the article")

class NewsSearchResults(BaseModel):
    articles: List[NewsArticle] = Field(description="List of news articles")



def invoke_claude(prompt: str, model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0", max_tokens: int = 500, temperature: float = 0.0) -> str:
    """Invokes Claude via the Bedrock API using the Messages API."""

    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name=AWS_REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
         ],
        "temperature": temperature
    })

    response = bedrock_runtime.invoke_model(
        modelId=model_id, body=body, contentType="application/json", accept="application/json"
    )
    response_body = json.loads(response.get("body").read())
    return response_body.get("content")[0].get("text")



def classify_news_intent(user_input: str) -> NewsSearchRequest:
    """Classifies the user's news search intent using Claude."""

    topics_str = str(list(topic_keywords.keys()))

    prompt = f"""You are a news search assistant. Classify the user's intent into one of the following search types: 'keyphrase', 'topic', or 'general'.

    Prioritize 'keyphrase' search whenever specific keyphrases are present in the user's query. Only classify as 'topic' if the query clearly indicates a general subject area and lacks specific keyphrases.

    Only classify as 'topic' if the query clearly indicates a general subject area *and* matches one of the provided topics. Do not infer broader topic categories.

    Based on the search type:
    - If 'keyphrase', extract a list of keyphrases.
    - If 'topic', extract a list of topics from: {topics_str}.
    - If 'general', no further information is needed.

    Return a JSON object with the following keys:
    - search_type: (string) The search type ('keyphrase', 'topic', or 'general'). # Changed 'keyword' to 'keyphrase'
    - keyphrases: (list of strings) The list of keyphrases (or an empty list). # Renamed keywords to keyphrases
    - topics: (list of strings)  The list of topics (or an empty list).

    Do NOT include any additional text outside the JSON object.

    User Input: {user_input}"""

    response_text = invoke_claude(prompt)

    try:
        response_json = json.loads(response_text)
        news_request = NewsSearchRequest(**response_json)
        return news_request
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error parsing Claude response: {e}")
        print(f"Raw response: {response_text}")
        return NewsSearchRequest(search_type="general")



def fetch_news(news_request: NewsSearchRequest) -> NewsSearchResults:
    """Fetches news articles based on the classified intent."""
    if news_request.search_type == "keyphrase":
        news_items = keyphrase_search(news_request.keyphrases)
    elif news_request.search_type == "topic":
        news_items = topic_search(news_request.topics, topic_keywords)
    else:
        news_items = general_search()

    articles = [NewsArticle(**item) for item in news_items]
    return NewsSearchResults(articles=articles)


def process_input(user_input: str) -> Tuple[Optional[NewsSearchRequest], Union[NewsSearchResults, str]]:
    """Processes user input, checks relevance, classifies intent, and fetches news."""

    news_request = classify_news_intent(user_input)
    news_result = fetch_news(news_request)
    return news_request, news_result


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    articles = []
    error_message = None
    user_input_display = None
    search_type_display = None
    search_terms_display = None

    if request.method == 'POST':
        user_input = request.form['user_input']
        user_input_display = user_input
        news_request, news_result = process_input(user_input)

        if news_request:
            search_type_display = news_request.search_type
            if news_request.search_type == 'keyphrase':
                search_terms_display = ", ".join(news_request.keyphrases)
            elif news_request.search_type == 'topic':
                search_terms_display = ", ".join(news_request.topics)
            else:
                search_terms_display = "General Search"


        if isinstance(news_result, str):
            articles = []
            error_message = news_result
        elif len(news_result.articles) == 0:
             articles = []
             error_message = 'I could not find any article containing your search terms from major news outlets in the last 2 days.'
        else:
            articles = []
            error_message = None
            for article in news_result.articles:
                articles.append({
                    'title': article.title,
                    'publisher': article.publisher,
                    'time': article.time,
                    'url': article.url
                })
            articles = sorted(articles, key = lambda x: x['time'], reverse=True)

        return render_template('index.html',
                               articles=articles,
                               error_message=error_message,
                               user_input=user_input_display,
                               search_type=search_type_display,
                               search_terms=search_terms_display
                               )
    return render_template('index.html',
                           articles=None,
                           error_message=None,
                           user_input=None,
                           search_type=None,
                           search_terms=None
                           )

if __name__ == '__main__':
    app.run(debug=True)