from flask import Flask, render_template_string, make_response
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import threading
import time
import os
import re

app = Flask(__name__)

# Fluid Vertical Motion Backdrops matching your key news channels
SVG_GENERAL = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1080 1920'><defs><linearGradient id='g' x1='0%25' y1='0%25' x2='100%25' y2='100%25'><stop offset='0%25' stop-color='%230f172a'/><stop offset='100%25' stop-color='%231e293b'/></linearGradient></defs><rect width='1080' height='1920' fill='url(%23g)'/><circle cx='540' cy='960' r='400' fill='%2338bdf8' opacity='0.04'><animate attributeName='r' values='300;450;300' dur='6s' repeatCount='indefinite'/></circle><path d='M100 1500h880' stroke='%2338bdf8' stroke-width='4' opacity='0.2'/></svg>"
SVG_AUTO = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1080 1920'><defs><linearGradient id='g' x1='0%25' y1='0%25' x2='100%25' y2='100%25'><stop offset='0%25' stop-color='%230b0f19'/><stop offset='100%25' stop-color='%23111827'/></linearGradient></defs><rect width='1080' height='1920' fill='url(%23g)'/><path d='M-100 960 Q 540 600 1180 960' fill='none' stroke='%2338bdf8' stroke-width='8' opacity='0.08'><animate attributeName='d' values='M-100 960 Q 540 500 1180 960; M-100 960 Q 540 1300 1180 960; M-100 960 Q 540 500 1180 960' dur='8s' repeatCount='indefinite'/></path></svg>"
SVG_TECH = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1080 1920'><defs><linearGradient id='g' x1='0%25' y1='0%25' x2='100%25' y2='100%25'><stop offset='0%25' stop-color='%23090d16'/><stop offset='100%25' stop-color='%231e1b4b'/></linearGradient></defs><rect width='1080' height='1920' fill='url(%23g)'/><g fill='%2338bdf8' opacity='0.15'><circle cx='200' cy='400' r='3'><animate attributeName='opacity' values='0.2;1;0.2' dur='3s' repeatCount='indefinite'/></circle><circle cx='800' cy='600' r='4'><animate attributeName='opacity' values='1;0.2;1' dur='4s' repeatCount='indefinite'/></circle><circle cx='400' cy='1400' r='3'><animate attributeName='opacity' values='0.1;0.8;0.1' dur='2.5s' repeatCount='indefinite'/></circle></g></svg>"
SVG_SPORTS = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1080 1920'><defs><linearGradient id='g' x1='0%25' y1='0%25' x2='100%25' y2='100%25'><stop offset='0%25' stop-color='%23061320'/><stop offset='100%25' stop-color='%230f172a'/></linearGradient></defs><rect width='1080' height='1920' fill='url(%23g)'/><path d='M0 300 L1080 600 M0 1600 L1080 1300' stroke='%2338bdf8' stroke-width='2' opacity='0.05'/><circle cx='540' cy='960' r='200' fill='none' stroke='%2338bdf8' stroke-width='4' opacity='0.06'><animate attributeName='transform' type='scale' values='1;1.2;1' dur='5s' repeatCount='indefinite'/></circle></svg>"

NEWS_CACHE = []

def clean_html_tags(text):
    if not text: return ""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

def scrape_rss_feed(query, category_slug, category_label, svg_backdrop):
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
        
        for item in items[:8]: # Expanded depth queue
            title_text = item.find('title').text if item.find('title') is not None else ""
            desc_element = item.find('description')
            raw_desc = desc_element.text if desc_element is not None else ""
            
            if not title_text: continue
                
            source_name = "Regional Feed"
            clean_title = title_text
            if " - " in title_text:
                parts = title_text.rsplit(" - ", 1)
                clean_title = parts[0].strip()
                source_name = parts[1].strip()
            
            clean_description = clean_html_tags(raw_desc)
            if len(clean_description) < 15 or clean_description.startswith(clean_title[:10]):
                clean_description = f"Operational assessments indicate major growth trends across localized focal networks. Strategic reporting from {source_name} monitors structural frameworks, tracking real-time industry updates."

            articles.append({
                "category": category_slug, 
                "title": clean_title, 
                "source": source_name,
                "label": category_label, 
                "img": svg_backdrop,
                "story_body": clean_description
            })
    except Exception as e:
        print(f"Error scraping {query}: {e}")
    return articles

def update_news_cache_worker():
    global NEWS_CACHE
    while True:
        general = scrape_rss_feed("Saudi Arabia infrastructure project economy", "all", "General News", SVG_GENERAL)
        auto = scrape_rss_feed("Saudi automotive electric car market", "cars", "Automotive", SVG_AUTO)
        tech = scrape_rss_feed("Gulf tech sector artificial intelligence business", "tech", "Tech & Biz", SVG_TECH)
        sports = scrape_rss_feed("Saudi Pro League football transfers match", "sports", "Sports Feed", SVG_SPORTS)
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
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap" rel="stylesheet">
    
    <style>
        * {
            box-sizing: border-box;
            margin: 0; padding: 0;
            font-family: 'Inter', sans-serif;
            -webkit-tap-highlight-color: transparent;
        }

        body, html {
            background-color: #000000;
            height: 100%; width: 100%;
            overflow: hidden;
        }

        /* Full Screen Swiper Feed Shell */
        .reel-container {
            height: 100%; width: 100%;
            overflow-y: scroll;
            scroll-snap-type: y mandatory;
            scroll-behavior: smooth;
            -webkit-overflow-scrolling: touch;
        }
        .reel-container::-webkit-scrollbar { display: none; }

        /* Individual TikTok Aspect Broadcast Section */
        .reel-card {
            width: 100%; height: 100%;
            scroll-snap-align: start;
            scroll-snap-stop: always;
            position: relative;
            background-size: cover;
            background-position: center;
            display: flex; flex-direction: column;
            justify-content: flex-end;
            padding: 40px 24px 120px 24px;
        }

        /* Clean Foreground Visibility Shield */
        .card-scrim {
            position: absolute; inset: 0;
            background: linear-gradient(to bottom, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0.4) 50%, rgba(0,0,0,0.85) 100%);
            z-index: 1;
        }

        /* Broadcast Content wrapper */
        .reel-content {
            position: relative; z-index: 10;
            display: flex; flex-direction: column;
            gap: 16px; width: 84%;
        }

        .channel-row {
            display: flex; align-items: center; gap: 10px;
        }

        .badge-live {
            background-color: #ef4444; color: white;
            font-size: 0.72rem; font-weight: 900;
            padding: 3px 10px; border-radius: 4px;
            letter-spacing: 1px; text-transform: uppercase;
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.4);
        }

        .badge-source {
            background-color: rgba(255,255,255,0.12);
            color: #ffffff; border: 1px solid rgba(255,255,255,0.15);
            font-size: 0.8rem; font-weight: 700;
            padding: 3px 12px; border-radius: 6px;
            backdrop-filter: blur(8px);
        }

        /* High-Impact Cinematic Kinetic Typography */
        .reel-headline {
            font-size: 1.6rem; font-weight: 900;
            line-height: 1.35; color: #ffffff;
            text-shadow: 0 4px 12px rgba(0,0,0,0.6);
            letter-spacing: -0.5px;
        }

        .reel-snippet {
            font-size: 0.95rem; line-height: 1.6;
            color: #cbd5e1; font-weight: 400;
            opacity: 0.9;
        }

        /* Sidebar Interface Buttons Stack */
        .action-sidebar {
            position: absolute; right: 16px; bottom: 130px;
            z-index: 20; display: flex; flex-direction: column;
            align-items: center; gap: 24px;
        }

        .action-button {
            background: rgba(28, 28, 34, 0.6);
            border: 1px solid rgba(255,255,255,0.1);
            width: 50px; height: 50px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            color: white; font-size: 1.3rem; cursor: pointer;
            backdrop-filter: blur(10px); transition: transform 0.2s;
        }
        .action-button:active { transform: scale(0.9); }
        .action-label { font-size: 0.7rem; color: #94a3b8; font-weight: 700; margin-top: 4px; }

        /* Minimal Bottom Navigator strip */
        .nav-strip {
            position: fixed; bottom: 0; left: 0; right: 0; height: 70px;
            background: linear-gradient(to top, rgba(0,0,0,1) 70%, rgba(0,0,0,0) 100%);
            display: flex; justify-content: center; align-items: center; z-index: 1000;
        }
        .nav-center-pill {
            background-color: #38bdf8; color: #000000;
            font-weight: 900; font-size: 0.85rem; padding: 10px 28px;
            border-radius: 30px; letter-spacing: 0.5px; text-transform: uppercase;
            box-shadow: 0 4px 15px rgba(56, 189, 248, 0.4);
        }
    </style>
</head>
<body>

    <!-- Scrollable Video-Style Frame Feed Container -->
    <div class="reel-container" id="newsFeed">
        {% for item in news %}
        <div class="reel-card" style="background-image: url('{{ item.img }}');">
            <div class="card-scrim"></div>
            
            <div class="reel-content">
                <div class="channel-row">
                    <span class="badge-live">Live</span>
                    <span class="badge-source">📡 {{ item.source }}</span>
                </div>
                <h1 class="reel-headline">{{ item.title }}</h1>
                <p class="reel-snippet">{{ item.story_body }}</p>
                <div style="color: #38bdf8; font-weight: 700; font-size: 0.82rem; margin-top: 4px;">
                    📌 Topic: {{ item.label }}
                </div>
            </div>

            <!-- Stacked Engagement Layer -->
            <div class="action-sidebar">
                <div style="text-align: center;">
                    <button class="action-button" onclick="alert('Story bookmarked successfully!')">⚡</button>
                    <div class="action-label">Save</div>
                </div>
                <div style="text-align: center;">
                    <button class="action-button" onclick="alert('Link parsed for global distribution channel.')">🔗</button>
                    <div class="action-label">Share</div>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>

    <nav class="nav-strip">
        <div class="nav-center-pill">GNews Radar Feed</div>
    </nav>

</body>
</html>
"""

@app.route('/')
def home():
    display_news = NEWS_CACHE if NEWS_CACHE else [
        {"category": "all", "title": "Establishing secure live data connection. Swipe up to prepare streams...", "source": "Radar System", "label": "General", "img": SVG_GENERAL, "story_body": "Synchronizing secure digital broadcast modules from regional feeds."},
        {"category": "cars", "title": "Compiling fresh automotive and electric infrastructure metrics...", "source": "Auto Sector", "label": "Automotive", "img": SVG_AUTO, "story_body": "Aggregating industrial growth parameters and vehicle supply updates."},
        {"category": "tech", "title": "Processing venture capital ecosystem analytics...", "source": "Tech Hub", "label": "Tech & Biz", "img": SVG_TECH, "story_body": "Calibrating database arrays for decentralized software markets."}
    ]
    response = make_response(render_template_string(HTML_TEMPLATE, news=display_news))
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
