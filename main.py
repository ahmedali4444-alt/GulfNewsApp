from flask import Flask, render_template_string, make_response
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import threading
import time
import os

app = Flask(__name__)

# Inline vector SVGs to maintain maximum rendering performance and safety on Android
SVG_GENERAL = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='12' fill='%231e293b'/><path d='M20 80V40h15v40H20zm20 0V20h15v40H40zm20 0V50h15v30H60zm20 0V35h10v45H80z' fill='%2338bdf8' opacity='0.7'/><line x1='10' y1='80' x2='90' y2='80' stroke='%2394a3b8' stroke-width='2'/></svg>"
SVG_AUTO = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='12' fill='%231e293b'/><path d='M15 55l10-15h50l10 15h5v15H10V55h5zm15 15a7 7 0 1 0 0-14 7 7 0 0 0 0 14zm40 0a7 7 0 1 0 0-14 7 7 0 0 0 0 14z' fill='%2338bdf8' opacity='0.8'/></svg>"
SVG_TECH = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='12' fill='%231e293b'/><rect x='25' y='25' width='50' height='40' rx='3' fill='none' stroke='%2338bdf8' stroke-width='4'/><path d='M20 75h60v4H20zM45 65h10v10H45z' fill='%2338bdf8'/><circle cx='50' cy='45' r='5' fill='%2338bdf8' opacity='0.5'/></svg>"
SVG_SPORTS = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='12' fill='%231e293b'/><circle cx='50' cy='50' r='25' fill='none' stroke='%2338bdf8' stroke-width='3'/><path d='M32 32l10 10zm36 0L58 42zm0 36L58 58zm-36 0l10-10z' stroke='%2338bdf8' stroke-width='3'/><circle cx='50' cy='50' r='6' fill='%2338bdf8'/></svg>"

# Global cache to keep app delivery instantaneous
NEWS_CACHE = []

def scrape_rss_feed(query, category_slug, category_label, svg_icon):
    articles = []
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en&gl=SA&ceid=SA:en"
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=8) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        items = root.findall('./channel/item')
        
        for item in items[:6]:  # Keep the top 6 freshest items per category
            title_text = item.find('title').text if item.find('title') is not None else ""
            link_text = item.find('link').text if item.find('link') is not None else "https://news.google.com"
            
            if not title_text:
                continue
                
            source_name = "Regional Feed"
            clean_title = title_text
            if " - " in title_text:
                parts = title_text.rsplit(" - ", 1)
                clean_title = parts[0].strip()
                source_name = parts[1].strip()
                
            articles.append({
                "category": category_slug,
                "title": clean_title,
                "source": source_name,
                "label": category_label,
                "img": svg_icon,
                "url": link_text
            })
    except Exception as e:
        print(f"Error scraping {query}: {e}")
    return articles

def update_news_cache_worker():
    global NEWS_CACHE
    while True:
        print("Starting background news synchronization...")
        
        # Pull live feeds cleanly using geo-focused keywords
        general = scrape_rss_feed("Saudi Arabia infrastructure economy", "all", "General", SVG_GENERAL)
        auto = scrape_rss_feed("Saudi automotive electric vehicles", "cars", "Automotive", SVG_AUTO)
        tech = scrape_rss_feed("Gulf tech startups business", "tech", "Tech & Biz", SVG_TECH)
        sports = scrape_rss_feed("Saudi Pro League football", "sports", "Sports", SVG_SPORTS)
        
        combined_news = general + auto + tech + sports
        
        if combined_news:
            NEWS_CACHE = combined_news
            print("News synchronization completed successfully.")
        else:
            print("Sync returned empty fields. Retaining older cached entries.")
            
        # Sleep for 1 hour (3600 seconds) before quietly checking for updates again
        time.sleep(3600)

# Trigger the background worker thread immediately upon server ignition
thread = threading.Thread(target=update_news_cache_worker, daemon=True)
thread.start()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>GNews Radar</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg-color: #0f0f13;
            --surface-color: #1c1c22;
            --primary-color: #38bdf8;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: #2e2e38;
        }

        * {
            box-sizing: border-box;
            margin: 0; padding: 0;
            font-family: 'Inter', sans-serif;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            padding-top: 75px; padding-bottom: 90px;
            overflow-x: hidden;
        }

        .top-header {
            position: fixed; top: 0; left: 0; right: 0; height: 65px;
            background-color: #1c1c22; display: flex; align-items: center;
            justify-content: space-between; padding: 0 20px;
            border-bottom: 1px solid var(--border-color); z-index: 1000;
        }

        .nav-btn { background: none; border: none; color: var(--text-main); font-size: 1.1rem; cursor: pointer; visibility: hidden; }
        .lang-btn { background: none; border: none; color: var(--text-main); font-size: 1.3rem; cursor: pointer; }
        .app-title { font-size: 1.25rem; font-weight: 800; color: var(--text-main); }

        .category-container {
            padding: 15px 20px 20px 20px;
            display: flex; gap: 12px;
            overflow-x: auto; white-space: nowrap;
        }
        .category-container::-webkit-scrollbar { display: none; }

        .chip {
            background-color: var(--surface-color); color: var(--text-muted);
            padding: 8px 22px; border-radius: 25px; font-size: 0.9rem;
            font-weight: 700; border: 1px solid var(--border-color); cursor: pointer;
        }

        .chip.active {
            background-color: var(--primary-color); color: #0f0f13; border-color: var(--primary-color);
        }

        .screen { display: none; padding: 0 20px; }
        .screen.active { display: block; }

        .news-feed { display: flex; flex-direction: column; gap: 14px; }

        .news-card {
            background-color: var(--surface-color); border-radius: 16px;
            padding: 16px; border: 1px solid var(--border-color);
            box-shadow: 0 6px 18px rgba(0,0,0,0.12); cursor: pointer;
            display: flex; gap: 15px; align-items: flex-start;
            transition: background-color 0.2s;
        }
        .news-card:active { background-color: #24242e; }

        .news-content-wrapper { flex-grow: 1; display: flex; flex-direction: column; gap: 8px; }

        .news-image-wrapper { width: 80px; height: 80px; flex-shrink: 0; border-radius: 12px; overflow: hidden; }
        .news-image-wrapper img { width: 100%; height: 100%; object-fit: fill; }

        .source-badge {
            align-self: flex-start; background-color: rgba(56, 189, 248, 0.08);
            color: var(--primary-color); padding: 2px 8px; border-radius: 6px;
            font-size: 0.72rem; font-weight: 700;
        }

        .news-card h3 { font-size: 1.02rem; line-height: 1.45; color: var(--text-main); font-weight: 700; }

        .card-footer {
            display: flex; justify-content: space-between; align-items: center;
            font-size: 0.8rem; color: var(--text-muted); border-top: 1px solid var(--border-color);
            padding-top: 8px; margin-top: 4px;
        }

        .read-more { color: var(--primary-color); font-weight: 700; font-size: 0.8rem; }

        .bottom-nav {
            position: fixed; bottom: 0; left: 0; right: 0; height: 75px;
            background-color: #141418; border-top: 1px solid var(--border-color);
            display: flex; justify-content: space-around; align-items: center; z-index: 1000;
        }

        .nav-item {
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            color: var(--text-muted); background: none; border: none; font-size: 0.8rem;
            font-weight: 700; width: 33%; gap: 5px;
        }
        .nav-item.active { color: var(--primary-color); }
        
        .placeholder-view { text-align: center; padding: 60px 20px; }
        .placeholder-view h2 { color: var(--text-main); margin-bottom: 12px; }
    </style>
</head>
<body>

    <header class="top-header">
        <button class="nav-btn" id="backBtn" onclick="goToHome()">⬅️ Back</button>
        <div class="app-title" id="mainHeaderTitle">GNews Radar</div>
        <button class="lang-btn">ℹ️</button>
    </header>

    <main id="homeScreen" class="screen active">
        <div class="category-container">
            <div class="chip active" onclick="filterCategory('all', this)">Top News</div>
            <div class="chip" onclick="filterCategory('cars', this)">Automotive</div>
            <div class="chip" onclick="filterCategory('tech', this)">Tech & Business</div>
            <div class="chip" onclick="filterCategory('sports', this)">Sports</div>
        </div>

        <div class="news-feed" id="newsFeed">
            {% for item in news %}
            <div class="news-card" data-category="{{ item.category }}" onclick="window.location.href='{{ item.url }}';">
                <div class="news-content-wrapper">
                    <div class="source-badge">📰 {{ item.source }}</div>
                    <h3>{{ item.title }}</h3>
                    <div class="card-footer">
                        <span>🏷️ {{ item.label }}</span>
                        <span class="read-more">Read More ➡️</span>
                    </div>
                </div>
                <div class="news-image-wrapper">
                    <img src="{{ item.img }}" alt="Topic Image">
                </div>
            </div>
            {% endfor %}
        </div>
    </main>

    <section id="profileScreen" class="screen">
        <div class="placeholder-view">
            <h2>👤 Profile Dashboard</h2>
            <p style="color: var(--text-muted); margin-top: 8px;">Welcome to your personalized GNews Radar account control space.</p>
        </div>
    </section>

    <section id="settingsScreen" class="screen">
        <div class="placeholder-view">
            <h2>⚙️ System Settings</h2>
            <p style="color: var(--text-muted); margin-top: 8px;">Configure reading display metrics, background synchronization, and push configurations.</p>
        </div>
    </section>

    <nav class="bottom-nav">
        <button class="nav-item active" id="tab-home" onclick="switchTab('home')">
            <span>🏠</span><span>Home</span>
        </button>
        <button class="nav-item" id="tab-profile" onclick="switchTab('profile')">
            <span>👤</span><span>Profile</span>
        </button>
        <button class="nav-item" id="tab-settings" onclick="switchTab('settings')">
            <span>⚙️</span><span>Settings</span>
        </button>
    </nav>

    <script>
        function filterCategory(category, element) {
            document.querySelectorAll('.chip').forEach(chip => chip.classList.remove('active'));
            element.classList.add('active');

            const cards = document.querySelectorAll('.news-card');
            cards.forEach(card => {
                if (category === 'all' || card.getAttribute('data-category') === category) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        }

        function switchTab(screenName) {
            const titles = { 'home': 'GNews Radar', 'profile': 'User Profile', 'settings': 'Preferences' };
            document.getElementById('mainHeaderTitle').innerText = titles[screenName];

            document.querySelectorAll('.screen').forEach(scr => scr.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(tab => tab.classList.remove('active'));

            document.getElementById(screenName + 'Screen').classList.add('active');
            document.getElementById('tab-' + screenName).classList.add('active');

            document.getElementById('backBtn').style.visibility = screenName === 'home' ? 'hidden' : 'visible';
        }

        function goToHome() { switchTab('home'); }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    # Instantly read from memory cache. Fall back to placeholder array if cache is filling up
    display_news = NEWS_CACHE if NEWS_CACHE else [
        {"category": "all", "title": "Synchronizing latest news streams. Pull down to refresh...", "source": "System", "label": "General", "img": SVG_GENERAL, "url": "#"},
        {"category": "cars", "title": "Updating live automotive insights from local markets...", "source": "System", "label": "Automotive", "img": SVG_AUTO, "url": "#"},
        {"category": "tech", "title": "Parsing data for regional technology sectors...", "source": "System", "label": "Tech & Biz", "img": SVG_TECH, "url": "#"},
        {"category": "sports", "title": "Fetching updated match lists and team schedules...", "source": "System", "label": "Sports", "img": SVG_SPORTS, "url": "#"}
    ]
    
    response = make_response(render_template_string(HTML_TEMPLATE, news=display_news))
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
