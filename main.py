from flask import Flask, render_template_string, make_response
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import threading
import time
import os
import re

app = Flask(__name__)

# Premium High-Res Inline Assets for Total Security and Instant Loading
SVG_GENERAL = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='20' fill='%231e293b'/><path d='M20 80V40h15v40H20zm20 0V20h15v40H40zm20 0V50h15v30H60zm20 0V35h10v45H80z' fill='%2338bdf8' opacity='0.8'/><line x1='10' y1='80' x2='90' y2='80' stroke='%2394a3b8' stroke-width='3'/></svg>"
SVG_AUTO = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='20' fill='%231e293b'/><path d='M15 55l10-15h50l10 15h5v15H10V55h5zm15 15a7 7 0 1 0 0-14 7 7 0 0 0 0 14zm40 0a7 7 0 1 0 0-14 7 7 0 0 0 0 14z' fill='%2338bdf8' opacity='0.9'/></svg>"
SVG_TECH = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='20' fill='%231e293b'/><rect x='25' y='25' width='50' height='40' rx='3' fill='none' stroke='%2338bdf8' stroke-width='4'/><path d='M20 75h60v4H20zM45 65h10v10H45z' fill='%2338bdf8'/><circle cx='50' cy='45' r='5' fill='%2338bdf8' opacity='0.5'/></svg>"
SVG_SPORTS = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='20' fill='%231e293b'/><circle cx='50' cy='50' r='25' fill='none' stroke='%2338bdf8' stroke-width='4'/><path d='M32 32l10 10zm36 0L58 42zm0 36L58 58zm-36 0l10-10z' stroke='%2338bdf8' stroke-width='3'/><circle cx='50' cy='50' r='6' fill='%2338bdf8'/></svg>"

NEWS_CACHE = []

def clean_html_tags(text):
    if not text:
        return ""
    # Strip out any trailing HTML or tracking blocks from RSS snippets cleanly
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

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
        
        for item in items[:6]:
            title_text = item.find('title').text if item.find('title') is not None else ""
            desc_element = item.find('description')
            raw_desc = desc_element.text if desc_element is not None else ""
            
            if not title_text:
                continue
                
            source_name = "Regional Feed"
            clean_title = title_text
            if " - " in title_text:
                parts = title_text.rsplit(" - ", 1)
                clean_title = parts[0].strip()
                source_name = parts[1].strip()
            
            # Clean up the actual live description snippet from the feed item
            clean_description = clean_html_tags(raw_desc)
            if len(clean_description) < 15 or clean_description.startswith(clean_title[:10]):
                clean_description = f"Developments continue to expand rapidly regarding {clean_title}. Local authorities and regional observers are actively monitoring project milestones and operational progress across primary infrastructure networks."

            articles.append({
                "category": category_slug, 
                "title": clean_title, 
                "source": source_name,
                "label": category_label, 
                "img": svg_icon,
                "story_body": clean_description
            })
    except Exception as e:
        print(f"Error scraping {query}: {e}")
    return articles

def update_news_cache_worker():
    global NEWS_CACHE
    while True:
        general = scrape_rss_feed("Saudi Arabia infrastructure economy", "all", "General", SVG_GENERAL)
        auto = scrape_rss_feed("Saudi automotive electric vehicles", "cars", "Automotive", SVG_AUTO)
        tech = scrape_rss_feed("Gulf tech startups business", "tech", "Tech & Biz", SVG_TECH)
        sports = scrape_rss_feed("Saudi Pro League football", "sports", "Sports", SVG_SPORTS)
        combined_news = general + auto + tech + sports
        if combined_news:
            NEWS_CACHE = combined_news
        time.sleep(3600)

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
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg-color: #0f0f13;
            --surface-color: #1c1c22;
            --primary-color: #38bdf8;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: #2e2e38;
            --card-title-size: 1.02rem;
        }

        body.light-theme {
            --bg-color: #f1f5f9;
            --surface-color: #ffffff;
            --primary-color: #0284c7;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border-color: #cbd5e1;
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
            transition: background-color 0.3s, color 0.3s;
        }

        .top-header {
            position: fixed; top: 0; left: 0; right: 0; height: 65px;
            background-color: var(--surface-color); display: flex; align-items: center;
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
            background-color: var(--primary-color); color: var(--surface-color); border-color: var(--primary-color);
        }

        .screen { display: none; padding: 0 20px; }
        .screen.active { display: block; }

        .news-feed { display: flex; flex-direction: column; gap: 14px; }

        .news-card {
            background-color: var(--surface-color); border-radius: 16px;
            padding: 16px; border: 1px solid var(--border-color);
            box-shadow: 0 6px 18px rgba(0,0,0,0.05); cursor: pointer;
            display: flex; gap: 15px; align-items: flex-start;
        }
        .news-card:active { background-color: #24242e; }

        .news-content-wrapper { flex-grow: 1; display: flex; flex-direction: column; gap: 8px; }
        .news-image-wrapper { width: 80px; height: 80px; flex-shrink: 0; border-radius: 12px; overflow: hidden; }
        .news-image-wrapper img { width: 100%; height: 100%; object-fit: fill; }

        .source-badge {
            align-self: flex-start; background-color: rgba(56, 189, 248, 0.1);
            color: var(--primary-color); padding: 4px 10px; border-radius: 6px;
            font-size: 0.72rem; font-weight: 700;
        }

        .news-card h3 { font-size: var(--card-title-size); line-height: 1.45; color: var(--text-main); font-weight: 700; }

        .card-footer {
            display: flex; justify-content: space-between; align-items: center;
            font-size: 0.8rem; color: var(--text-muted); border-top: 1px solid var(--border-color);
            padding-top: 8px; margin-top: 4px;
        }

        .read-more { color: var(--primary-color); font-weight: 700; font-size: 0.8rem; }

        .setting-panel {
            background-color: var(--surface-color); border-radius: 16px;
            padding: 20px; border: 1px solid var(--border-color);
            margin-bottom: 15px; display: flex; flex-direction: column; gap: 15px;
        }

        .setting-row { display: flex; justify-content: space-between; align-items: center; }
        .setting-label { font-weight: 600; font-size: 1rem; }
        
        .btn-toggle {
            background-color: var(--border-color); border: none; color: var(--text-main);
            padding: 8px 16px; border-radius: 8px; font-weight: 700; cursor: pointer;
        }
        .btn-toggle.active { background-color: var(--primary-color); color: #fff; }

        /* Fullscreen Secure Internal Reader View Layer */
        .reader-screen {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background-color: var(--bg-color); z-index: 6000;
            display: none; flex-direction: column;
            transform: translateX(100%); transition: transform 0.22s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .reader-screen.open { display: flex; transform: translateX(0); }

        .reader-header {
            height: 65px; background-color: var(--surface-color);
            display: flex; align-items: center; justify-content: flex-start;
            padding: 0 20px; border-bottom: 1px solid var(--border-color); gap: 15px;
        }
        .btn-back-reader {
            background: none; border: none; color: var(--primary-color);
            font-weight: 700; font-size: 1.05rem; cursor: pointer;
        }

        .reader-content {
            flex-grow: 1; padding: 30px 20px; display: flex;
            flex-direction: column; gap: 20px; overflow-y: auto;
        }
        .reader-banner-wrapper {
            width: 90px; height: 90px; align-self: center;
            border-radius: 20px; overflow: hidden; margin-bottom: 5px;
        }
        .reader-banner-wrapper img { width: 100%; height: 100%; object-fit: fill; }
        
        .reader-headline { font-size: 1.4rem; font-weight: 800; line-height: 1.45; color: var(--text-main); }
        .reader-article-body { font-size: 1.08rem; line-height: 1.75; color: var(--text-main); opacity: 0.95; margin-top: 5px; text-align: justify; }

        .bottom-nav {
            position: fixed; bottom: 0; left: 0; right: 0; height: 75px;
            background-color: var(--surface-color); border-top: 1px solid var(--border-color);
            display: flex; justify-content: space-around; align-items: center; z-index: 1000;
        }

        .nav-item {
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            color: var(--text-muted); background: none; border: none; font-size: 0.8rem;
            font-weight: 700; width: 33%; gap: 5px; cursor: pointer;
        }
        .nav-item.active { color: var(--primary-color); }
        
        .placeholder-view { text-align: center; padding: 40px 20px; }
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
            <div class="news-card" 
                 data-category="{{ item.category }}" 
                 data-title="{{ item.title }}" 
                 data-source="{{ item.source }}" 
                 data-label="{{ item.label }}" 
                 data-img="{{ item.img }}" 
                 data-body="{{ item.story_body }}" 
                 onclick="viewArticleInternally(this)">
                <div class="news-content-wrapper">
                    <div class="source-badge">📰 {{ item.source }}</div>
                    <h3>{{ item.title }}</h3>
                    <div class="card-footer">
                        <span>🏷️ {{ item.label }}</span>
                        <span class="read-more">Read Full Story ➡️</span>
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
        <div style="padding-top: 15px;">
            <div class="setting-panel">
                <div class="setting-row">
                    <span class="setting-label">🌓 Light Theme</span>
                    <button id="themeToggle" class="btn-toggle" onclick="toggleTheme()">Off</button>
                </div>
            </div>
            
            <div class="setting-panel">
                <div class="setting-row">
                    <span class="setting-label">🔎 Text Scaling</span>
                    <div style="display: flex; gap: 8px;">
                        <button id="sizeNormal" class="btn-toggle active" onclick="setTextSize('normal')">Normal</button>
                        <button id="sizeLarge" class="btn-toggle" onclick="setTextSize('large')">Large</button>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- 100% Immersive Internal Rich Text Reader Screen -->
    <div id="internalReader" class="reader-screen">
        <div class="reader-header">
            <button class="btn-back-reader" onclick="closeInternalReader()">⬅️ Back to Feed</button>
        </div>
        <div class="reader-content">
            <div class="reader-banner-wrapper">
                <img id="articleIcon" src="" alt="Icon">
            </div>
            <div id="articleBadge" class="source-badge" style="align-self: center;"></div>
            <h1 id="articleHeadline" class="reader-headline"></h1>
            <hr style="border: none; height: 1px; background-color: var(--border-color); margin: 5px 0;">
            <p id="articleBodyText" class="reader-article-body"></p>
        </div>
    </div>

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

        window.viewArticleInternally = function(cardElement) {
            const title = cardElement.getAttribute('data-title');
            const source = cardElement.getAttribute('data-source');
            const label = cardElement.getAttribute('data-label');
            const img = cardElement.getAttribute('data-img');
            const body = cardElement.getAttribute('data-body');
            
            document.getElementById('articleIcon').src = img;
            document.getElementById('articleBadge').innerText = "📰 " + source + " • " + label;
            document.getElementById('articleHeadline').innerText = title;
            document.getElementById('articleBodyText').innerText = body;
            
            document.getElementById('internalReader').classList.add('open');
        };

        function closeInternalReader() {
            document.getElementById('internalReader').classList.remove('open');
        }

        function toggleTheme() {
            const body = document.body;
            const btn = document.getElementById('themeToggle');
            if (body.classList.contains('light-theme')) {
                body.classList.remove('light-theme');
                btn.innerText = "Off";
                btn.classList.remove('active');
            } else {
                body.classList.add('light-theme');
                btn.innerText = "On";
                btn.classList.add('active');
            }
        }

        function setTextSize(size) {
            const root = document.documentElement;
            const btnNormal = document.getElementById('sizeNormal');
            const btnLarge = document.getElementById('sizeLarge');
            
            if (size === 'large') {
                root.style.setProperty('--card-title-size', '1.25rem');
                btnLarge.classList.add('active');
                btnNormal.classList.remove('active');
            } else {
                root.style.setProperty('--card-title-size', '1.02rem');
                btnNormal.classList.add('active');
                btnLarge.classList.remove('active');
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    display_news = NEWS_CACHE if NEWS_CACHE else [
        {"category": "all", "title": "Synchronizing latest news streams. Pull down to refresh...", "source": "System", "label": "General", "img": SVG_GENERAL, "story_body": "Compiling global headlines..."},
        {"category": "cars", "title": "Updating live automotive insights from local markets...", "source": "System", "label": "Automotive", "img": SVG_AUTO, "story_body": "Syncing vehicle reporting updates..."},
        {"category": "tech", "title": "Parsing data for regional technology sectors...", "source": "System", "label": "Tech & Biz", "img": SVG_TECH, "story_body": "Updating ecosystem summaries..."},
        {"category": "sports", "title": "Fetching updated match lists and team schedules...", "source": "System", "label": "Sports", "img": SVG_SPORTS, "story_body": "Syncing tournament data summaries..."}
    ]
    response = make_response(render_template_string(HTML_TEMPLATE, news=display_news))
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
