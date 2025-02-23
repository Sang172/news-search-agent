from gnews import GNews
import time

topic_keywords = {
    "politics": [
        "politics", "election", "government", "congress", "president",
        "legislation", "vote", "political scandal"
    ],
    "business and economy": [
        "business", "economy", "finance", "markets", "stocks",
        "inflation", "interest rates", "recession", "economic growth", "jobs"
    ],
    "sports": [
        "sports", "football", "basketball", "baseball", "soccer", "hockey",
        "olympics", "championship", "athlete", "team"
    ],
    "entertainment": [
        "entertainment", "movies", "television", "music", "celebrities",
        "hollywood", "streaming", "awards", "pop culture"
    ],
    "science and technology": [
        "science", "technology", "research", "innovation",
        "artificial intelligence", "AI", "space"
    ],
    "international": [
        "international", "world", "global", "foreign policy",
        "united nations", "China", "Russia", "Europe", "Middle East"
    ]
}

def filter_us_outlets(news_list):
    us_outlets = [
        "cnn", "fox", "cbs", "nbc news", "abc", "reuters",
        "associated press", "bloomberg", "wall street journal", "new york times",
        "washington post", "usa today", "los angeles times", "npr", "pbs",
        "espn", "sports illustrated", "bleacher report", 
        "variety", "hollywood reporter", "rolling stone", "entertainment weekly"
    ]

    us_outlets_lower = [outlet.lower() for outlet in us_outlets]
    filtered_news = []
    for article in news_list:
        if 'publisher' in article and 'title' in article['publisher']:
            publisher_name_lower = article['publisher']['title'].lower()
            if any(outlet in publisher_name_lower for outlet in us_outlets_lower):
                filtered_news.append(article)
    return filtered_news

def filter_fields(news_list):
    news = []
    for item in news_list:
        d = {}
        d['title'] = item['title']
        d['publisher'] = item ['publisher']['title']
        d['time'] = item['published date']
        d['url'] = item['url']
        if d not in news:
            news.append(d)
    return news

def general_search():
    gnews = GNews(language='en', country='US', period='2d', max_results=20)
    news_items = gnews.get_top_news()
    news_items = filter_us_outlets(news_items)
    news_items = filter_fields(news_items)
    return news_items

def topic_search(topics, topic_keywords):
    gnews = GNews(language='en', country='US', period='2d', max_results=5)
    news_items = []
    for topic in topics:
        keywords = topic_keywords[topic]
        for keyword in keywords:
            try:
                news = gnews.get_news(keyword)
                news = filter_us_outlets(news)
                news_items.extend(news)
            except Exception as e:
                print(f"  Error searching for {keyword}: {e}")
            time.sleep(0.5)
    news_items = filter_fields(news_items)
    return news_items

def keyword_search(keywords):
    gnews = GNews(language='en', country='US', period='2d', max_results=5)
    news_items = []
    for keyword in keywords:
        try:
            news = gnews.get_news(keyword)
            news = filter_us_outlets(news)
            news_items.extend(news)
        except Exception as e:
            print(f"  Error searching for {keyword}: {e}")
        time.sleep(0.5)
    news_items = filter_fields(news_items)
    return news_items