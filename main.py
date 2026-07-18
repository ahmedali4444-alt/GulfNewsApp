from flask import Flask, render_template_string
import urllib.request
import xml.etree.ElementTree as ET

app = Flask(__name__)

def fetch_premium_news(query, cat_slug, cat_name):
    articles = []
    url = f"https://news.google.com/rss/search?q={query}&hl=ar&gl=SA&ceid=SA:ar"
    
    # Category-based fallback high-res images to keep the feed beautiful if an article lacks a thumbnail
    placeholders = {
        "all": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400&q=80", # News
        "cars": "https://images.unsplash.com/photo-1617788138017-80ad40651399?w=400&q=80", # Cars
        "tech": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80", # Tech
        "sports": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=400&q=80" # Sports
    }
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
        
        root = ET.fromstring(xml_data)
        
        for item in root.findall('./channel/item')[:12]:
            title_full = item.find('title').text
            link = item.find('link').text
            
            source = "وكالات الأنباء"
            title = title_full
            if " - " in title_full:
                parts = title_full.rsplit(" - ", 1)
                title = parts[0].strip()
                source = parts[1].strip()

            # Dynamic source favicon image extraction to use as the card graphic
            img_url = f"https://www.google.com/s2/favicons?sz=128&domain={link}"
            if not link or "google.com" in link:
                img_url = placeholders.get(cat_slug, placeholders["all"])

            articles.append({
                "category": cat_slug,
                "title": title,
                "source": source,
                "time": cat_name,
                "url": link,
                "img": img_url
            })
    except Exception as e:
        print(f"Error fetching {query}: {e}")
        
    return articles

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>رادار أخبار الخليج | Premium</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">
    
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
            margin: 0;
            padding: 0;
            font-family: 'Cairo', sans-serif;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            padding-top: 75px;
            padding-bottom: 90px;
            overflow-x: hidden;
        }

        /* --- HEADER --- */
        .top-header {
            position: fixed;
            top: 0; left: 0; right: 0;
            height: 65px;
            background-color: rgba(28, 28, 34, 0.95);
            backdrop-filter: blur(12px);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            border-bottom: 1px solid var(--border-color);
            z-index: 1000;
        }

        .nav-btn { background: none; border: none; color: var(--text-main); font-size: 1.3rem; cursor: pointer; visibility: hidden; }
        .lang-btn { background: none; border: none; color: var(--text-main); font-size: 1.3rem; cursor: pointer; }
        .app-title { font-size: 1.25rem; font-weight: 800; color: var(--text-main); letter-spacing: 0.5px;}

        /* --- CATEGORIES --- */
        .category-container {
            padding: 15px 20px 20px 20px;
            display: flex;
            gap: 12px;
            overflow-x: auto;
            white-space: nowrap;
        }
        .category-container::-webkit-scrollbar { display: none; }

        .chip {
            background-color: var(--surface-color);
            color: var(--text-muted);
            padding: 8px 22px;
            border-radius: 25px;
            font-size: 0.95rem;
            font-weight: 700;
            border: 1px solid var(--border-color);
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .chip.active {
            background-color: var(--primary-color);
            color: #0f0f13;
            border-color: var(--primary-color);
            box-shadow: 0 4px 15px rgba(56, 189, 248, 0.25);
        }

        /* --- SCREENS --- */
        .screen { display: none; padding: 0 20px; }
        .screen.active { display: block; animation: fadeIn 0.4s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        /* --- NEWS CARDS WITH IMAGES --- */
        .news-feed { display: flex; flex-direction: column; gap: 14px; }

        .news-card {
            background-color: var(--surface-color);
            border-radius: 16px;
            padding: 16px;
            border: 1px solid var(--border-color);
            box-shadow: 0 6px 18px rgba(0,0,0,0.12);
            transition: transform 0.2s;
            cursor: pointer;
            display: flex;
            gap: 15px;
            align-items: flex-start;
        }

        .news-card:active { transform: scale(0.98); }

        /* Left side image container */
        .news-image-wrapper {
            width: 85px;
            height: 85px;
            flex-shrink: 0;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.05);
            background-color: rgba(255, 255, 255, 0.02);
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .news-image-wrapper img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        /* Right side text container */
        .news-content-wrapper {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }

        .source-badge {
            align-self: flex-start;
            background-color: rgba(56, 189, 248, 0.08);
            color: var(--primary-color);
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 0.72rem;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .news-card h3 {
            font-size: 1.05rem;
            line-height: 1.45;
            color: var(--text-main);
            margin-bottom: 10px;
            font-weight: 700;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .card-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.8rem;
            color: var(--text-muted);
            padding-top: 4px;
        }

        .read-more { color: var(--primary-color); font-weight: 700; font-size: 0.8rem; }

        /* --- BOTTOM NAV --- */
        .bottom-nav {
            position: fixed; bottom: 0; left: 0; right: 0; height: 75px;
            background-color: #141418; border-top: 1px solid var(--border-color);
            display: flex; justify-content: space-around; align-items: center;
            z-index: 1000; padding-bottom: env(safe-area-inset-bottom);
        }

        .nav-item {
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            color: var(--text-muted); background: none; border: none; font-size: 0.8rem;
            font-weight: 700; cursor: pointer; width: 33%; gap: 5px;
        }
        .nav-item .icon { font-size: 1.5rem; transition: transform 0.3s; }
        .nav-item.active { color: var(--primary-color); }
        .nav-item.active .icon { transform: translateY(-3px); }
        
        .placeholder-view { text-align: center; padding: 60px 20px; }
        .placeholder-view h2 { color: var(--text-main); margin-bottom: 12px; }
    </style>
</head>
<body>

    <header class="top-header">
        <button class="nav-btn" id="backBtn" onclick="goToHome()">⬅️</button>
        <div class="app-title" id="mainHeaderTitle">رادار أخبار الخليج</div>
        <button class="lang-btn">🔔</button>
    </header>

    <main id="homeScreen" class="screen active">
        <div class="category-container">
            <div class="chip active" onclick="filterCategory('all', this)">أهم الأخبار</div>
            <div class="chip" onclick="filterCategory('cars', this)">سيارات</div>
            <div class="chip" onclick="filterCategory('tech', this)">تقنية وأعمال</div>
            <div class="chip" onclick="filterCategory('sports', this)">رياضة</div>
        </div>

        <div class="news-feed" id="newsFeed">
            {% for item in news %}
            <div class="news-card" data-category="{{ item.category }}" onclick="window.open('{{ item.url }}', '_blank')">
                
                <!-- Right Side Content -->
                <div class="news-content-wrapper">
                    <div class="source-badge">📰 {{ item.source }}</div>
                    <h3>{{ item.title }}</h3>
                    <div class="card-footer">
                        <span>🏷️ {{ item.time }}</span>
                        <span class="read-more">التفاصيل ⬅️</span>
                    </div>
                </div>

                <!-- Left Side Picture Box -->
                <div class="news-image-wrapper">
                    <img src="{{ item.img }}" alt="News Thumbnail" onerror="this.src='https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=150&q=80';">
                </div>

            </div>
            {% endfor %}
        </div>
    </main>

    <section id="profileScreen" class="screen">
        <div class="placeholder-view">
            <h2>👤 الملف الشخصي</h2>
            <p style="color: var(--text-muted)">مرحباً بك في لوحة تحكم حسابك الشخصي لرادار الخليج.</p>
        </div>
    </section>

    <section id="settingsScreen" class="screen">
        <div class="placeholder-view">
            <h2>⚙️ الإعدادات العامة</h2>
            <p style="color: var(--text-muted)">تخصيص وضع القراءة، الإشعارات الفورية، ومزامنة المصادر الإخبارية.</p>
        </div>
    </section>

    <nav class="bottom-nav">
        <button class="nav-item active" id="tab-home" onclick="switchTab('home')">
            <span class="icon">🏠</span><span>الرئيسية</span>
        </button>
        <button class="nav-item" id="tab-profile" onclick="switchTab('profile')">
            <span class="icon">👤</span><span>حسابي</span>
        </button>
        <button class="nav-item" id="tab-settings" onclick="switchTab('settings')">
            <span class="icon">⚙️</span><span>الإعدادات</span>
        </button>
    </nav>

    <script>
        function filterCategory(category, element) {
            document.querySelectorAll('.chip').forEach(chip => chip.classList.remove('active'));
            element.classList.add('active');

            const cards = document.querySelectorAll('.news-card');
            cards.forEach(card => {
                if (category === 'all' || card.getAttribute('data-category') === category) {
                    card.style.display = 'flex'; /* Maintained flexbox layout on filter */
                } else {
                    card.style.display = 'none';
                }
            });
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function switchTab(screenName) {
            const titles = { 'home': 'رادار أخبار الخليج', 'profile': 'الملف الشخصي', 'settings': 'الإعدادات والمظهر' };
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
    breaking_news = fetch_premium_news("أخبار السعودية", "all", "أخبار عامة")
    cars_news = fetch_premium_news("سيارات", "cars", "سيارات")
    tech_news = fetch_premium_news("تقنية واقتصاد السعودية", "tech", "تقنية وأعمال")
    sports_news = fetch_premium_news("رياضة السعودية", "sports", "رياضة")
    
    all_news = breaking_news + cars_news + tech_news + sports_news
    return render_template_string(HTML_TEMPLATE, news=all_news)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
