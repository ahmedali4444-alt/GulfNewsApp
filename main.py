from flask import Flask, render_template_string
import feedparser
from bs4 import BeautifulSoup

app = Flask(__name__)

# Complete Gulf-targeted Arabic feeds across all your requested categories
FEEDS = {
    "General/Politics": "https://ara.reuters.com/news/topNews?rpc=401",
    "Sports": "https://www.alriyadh.com/rss.sports",
    "Cars": "https://www.saudiauto.com.sa/feed/",
    "Games": "https://ar.ign.com/feed.xml"  # IGN Middle East (Arabic Gaming Feed)
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gulf News App</title>
    <style>
        body { font-family: system-ui, sans-serif; background-color: #121212; color: #e0e0e0; margin: 0; padding: 15px; padding-bottom: 80px; }
        h1 { text-align: center; color: #fff; margin-bottom: 20px; font-size: 1.5rem; }
        
        /* Smooth horizontal scrolling category tabs */
        .nav-tabs { display: flex; overflow-x: auto; gap: 10px; padding-bottom: 15px; margin-bottom: 15px; border-bottom: 1px solid #333; }
        .nav-tabs a { background-color: #222; color: #aaa; padding: 8px 16px; border-radius: 20px; text-decoration: none; font-size: 0.9rem; white-space: nowrap; border: 1px solid #444; }
        .nav-tabs a:active, .nav-tabs a:hover { background-color: #1E90FF; color: white; border-color: #1E90FF; }
        
        .category-section { margin-top: 10px; }
        .category-title { color: #1E90FF; font-size: 1.3rem; border-right: 4px solid #1E90FF; padding-right: 10px; margin-bottom: 15px; }
        
        /* Card Layout */
        .card { background-color: #1e1e1e; padding: 16px; border-radius: 12px; margin-bottom: 15px; border: 1px solid #2a2a2a; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }
        .card h3 { margin: 0 0 8px 0; font-size: 1.1rem; line-height: 1.4; }
        .card a { color: #64B5F6; text-decoration: none; }
        .card p { font-size: 0.88rem; color: #aaaaaa; line-height: 1.6; margin: 0; }
    </style>
</head>
<body>
    <h1>📱 رادار أخبار الخليج</h1>
    
    <!-- Quick Jump Category Navigation -->
    <div class="nav-tabs">
        {% for cat_name in all_news.keys() %}
            <a href="#{{ cat_name }}">{{ cat_name }}</a>
        {% endfor %}
    </div>
    
    {% for cat_name, articles in all_news.items() %}
        <div id="{{ cat_name }}" class="category-section">
            <h2 class="category-title">{{ cat_name }}</h2>
            {% for item in articles %}
                <div class="card">
                    <h3><a href="{{ item.link }}" target="_blank">{{ item.title }}</a></h3>
                    <p>{{ item.summary }}</p>
                </div>
            {% endfor %}
        </div>
    {% endfor %}
</body>
</html>
"""

@app.route('/')
def home():
    all_news = {}
    for cat_name, url in FEEDS.items():
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:4]: # Top 4 posts per category
            raw_summary = entry.get('summary', '')
            clean_summary = BeautifulSoup(raw_summary, "html.parser").get_text() if raw_summary else ""
            articles.append({
                "title": entry.get('title', 'No Title'),
                "link": entry.get('link', '#'),
                "summary": clean_summary[:140] + "..." if len(clean_summary) > 140 else clean_summary
            })
        all_news[cat_name] = articles
    return render_template_string(HTML_TEMPLATE, all_news=all_news)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Flask, render_template_string
import feedparser
from bs4 import BeautifulSoup

app = Flask(__name__)

# Core feeds for the Gulf region
FEEDS = {
    "رياضة": "https://www.alriyadh.com/rss.sports",
    "سيارات": "https://www.saudiauto.com.sa/feed/",
    "أخبار عامة": "https://ara.reuters.com/news/topNews?rpc=401"
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تطبيق أخبار الخليج</title>
    <style>
        body { font-family: system-ui, sans-serif; background-color: #121212; color: #e0e0e0; margin: 0; padding: 15px; }
        h1 { text-align: center; color: #fff; margin-bottom: 25px; }
        .category-title { color: #1E90FF; border-bottom: 2px solid #1E90FF; padding-bottom: 5px; margin-top: 30px; }
        .card { background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #333; }
        .card h3 { margin: 0 0 10px 0; font-size: 1.15rem; }
        .card a { color: #64B5F6; text-decoration: none; }
        .card p { font-size: 0.9rem; color: #b0b0b0; line-height: 1.5; margin: 0; }
    </style>
</head>
<body>
    <h1>📱 رادار أخبار الخليج</h1>
    
    {% for cat_name, articles in all_news.items() %}
        <h2 class="category-title">{{ cat_name }}</h2>
        {% for item in articles %}
            <div class="card">
                <h3><a href="{{ item.link }}" target="_blank">{{ item.title }}</a></h3>
                <p>{{ item.summary }}</p>
            </div>
        {% endfor %}
    {% endfor %}
</body>
</html>
"""

@app.route('/')
def home():
    all_news = {}
    for cat_name, url in FEEDS.items():
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:4]: # Grab top 4 per category
            raw_summary = entry.get('summary', '')
            clean_summary = BeautifulSoup(raw_summary, "html.parser").get_text() if raw_summary else ""
            articles.append({
                "title": entry.get('title', 'بدون عنوان'),
                "link": entry.get('link', '#'),
                "summary": clean_summary[:150] + "..." if len(clean_summary) > 150 else clean_summary
            })
        all_news[cat_name] = articles
    return render_template_string(HTML_TEMPLATE, all_news=all_news)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

