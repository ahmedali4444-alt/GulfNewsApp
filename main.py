from flask import Flask, render_template_string, make_response
import os

app = Flask(__name__)

# Premium content with dedicated, topic-specific imagery and verified external source routing
def get_optimized_news():
    return [
        # General News
        {
            "category": "all", 
            "title": "Saudi Arabia Accelerates Massive Infrastructure and Smart City Projects", 
            "source": "Gulf News", 
            "label": "General", 
            "img": "https://images.unsplash.com/photo-1582407947304-fd86f028f716?w=250&auto=format&fit=crop&q=80",
            "url": "https://www.saudinews.gov.sa"
        },
        {
            "category": "all", 
            "title": "Digital Transformation Market Expected to See Historic Growth Across the Region", 
            "source": "Riyadh Hub", 
            "label": "General", 
            "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=250&auto=format&fit=crop&q=80",
            "url": "https://www.saudigazette.com.sa"
        },
        {
            "category": "all", 
            "title": "New Green Initiatives Launched to Expand Sustainable Urban Spaces", 
            "source": "Arabia Vision", 
            "label": "General", 
            "img": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=250&auto=format&fit=crop&q=80",
            "url": "https://www.arabnews.com"
        },
        
        # Automotive News
        {
            "category": "cars", 
            "title": "Ford Recalls Explorer Models Globally: Structural Safety Impact on Regional Markets", 
            "source": "Saudi Auto", 
            "label": "Automotive", 
            "img": "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=250&auto=format&fit=crop&q=80",
            "url": "https://saudiauto.com.sa/"
        },
        {
            "category": "cars", 
            "title": "Lincoln Project: Luxury Off-Roader Aims to Challenge Defender and Lexus GX", 
            "source": "Saudi Auto", 
            "label": "Automotive", 
            "img": "https://images.unsplash.com/photo-1617788138017-80ad40651399?w=250&auto=format&fit=crop&q=80",
            "url": "https://saudiauto.com.sa/"
        },
        {
            "category": "cars", 
            "title": "Electric Vehicle Charging Network Expands Across Major Eastern Province Highways", 
            "source": "Auto Review", 
            "label": "Automotive", 
            "img": "https://images.unsplash.com/photo-1563720223185-11003d516935?w=250&auto=format&fit=crop&q=80",
            "url": "https://saudiauto.com.sa/"
        },
        
        # Tech & Business
        {
            "category": "tech", 
            "title": "Gulf Tech Hubs Announce Massive Venture Capital Funding for Local AI Startups", 
            "source": "Tech Economy", 
            "label": "Tech & Biz", 
            "img": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=250&auto=format&fit=crop&q=80",
            "url": "https://www.arabnews.com"
        },
        {
            "category": "tech", 
            "title": "Cloud Computing Infrastructure Demand Surges Ahead of Quarter Three App rollouts", 
            "source": "Byte Insights", 
            "label": "Tech & Biz", 
            "img": "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=250&auto=format&fit=crop&q=80",
            "url": "https://www.saudigazette.com.sa"
        },
        {
            "category": "tech", 
            "title": "E-Commerce Logistics Platforms Optimize Delivery Networks in Jubail and Khobar", 
            "source": "Logistics Daily", 
            "label": "Tech & Biz", 
            "img": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=250&auto=format&fit=crop&q=80",
            "url": "https://www.arabnews.com"
        },
        
        # Sports
        {
            "category": "sports", 
            "title": "Gulf Clubs Accelerate Major Signings in Summer Transfer Window", 
            "source": "FilMarma", 
            "label": "Sports", 
            "img": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=250&auto=format&fit=crop&q=80",
            "url": "https://www.kooora.com/"
        },
        {
            "category": "sports", 
            "title": "Faisal Al-Qabbani Leads Day One of Hill Climb Championship Round 2", 
            "source": "Sport News", 
            "label": "Sports", 
            "img": "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=250&auto=format&fit=crop&q=80",
            "url": "https://www.kooora.com/"
        },
        {
            "category": "sports", 
            "title": "Regional Stadiums Upgrade Facilities to Prepare for Upcoming Championship Season", 
            "source": "Stadium Feed", 
            "label": "Sports", 
            "img": "https://images.unsplash.com/photo-1521533886411-e77515283b3f?w=250&auto=format&fit=crop&q=80",
            "url": "https://www.kooora.com/"
        }
    ]

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
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            padding-top: 75px;
            padding-bottom: 90px;
            overflow-x: hidden;
        }

        .top-header {
            position: fixed;
            top: 0; left: 0; right: 0;
            height: 65px;
            background-color: #1c1c22;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            border-bottom: 1px solid var(--border-color);
            z-index: 1000;
        }

        .nav-btn { background: none; border: none; color: var(--text-main); font-size: 1.1rem; cursor: pointer; visibility: hidden; }
        .lang-btn { background: none; border: none; color: var(--text-main); font-size: 1.3rem; cursor: pointer; }
        .app-title { font-size: 1.25rem; font-weight: 800; color: var(--text-main); }

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
            font-size: 0.9rem;
            font-weight: 700;
            border: 1px solid var(--border-color);
            cursor: pointer;
        }

        .chip.active {
            background-color: var(--primary-color);
            color: #0f0f13;
            border-color: var(--primary-color);
        }

        .screen { display: none; padding: 0 20px; }
        .screen.active { display: block; }

        .news-feed { display: flex; flex-direction: column; gap: 14px; }

        .news-card {
            background-color: var(--surface-color);
            border-radius: 16px;
            padding: 16px;
            border: 1px solid var(--border-color);
            box-shadow: 0 6px 18px rgba(0,0,0,0.12);
            cursor: pointer;
            display: flex;
            gap: 15px;
            align-items: flex-start;
            transition: background-color 0.2s;
        }
        .news-card:active {
            background-color: #24242e;
        }

        .news-content-wrapper {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .news-image-wrapper {
            width: 85px;
            height: 85px;
            flex-shrink: 0;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.05);
            background-color: #2e2e38;
        }

        .news-image-wrapper img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .source-badge {
            align-self: flex-start;
            background-color: rgba(56, 189, 248, 0.08);
            color: var(--primary-color);
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 0.72rem;
            font-weight: 700;
        }

        .news-card h3 {
            font-size: 1.02rem;
            line-height: 1.45;
            color: var(--text-main);
            font-weight: 700;
        }

        .card-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.8rem;
            color: var(--text-muted);
            border-top: 1px solid var(--border-color);
            padding-top: 8px;
            margin-top: 4px;
        }

        .read-more { color: var(--primary-color); font-weight: 700; font-size: 0.8rem; }

        .bottom-nav {
            position: fixed; bottom: 0; left: 0; right: 0; height: 75px;
            background-color: #141418; border-top: 1px solid var(--border-color);
            display: flex; justify-content: space-around; align-items: center;
            z-index: 1000;
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
            <!-- Entire card is clickable to easily trigger the web link on mobile viewports -->
            <div class="news-card" data-category="{{ item.category }}" onclick="window.open('{{ item.url }}', '_blank')">
                <div class="news-content-wrapper">
                    <div class="source-badge">📰 {{ item.source }}</div>
                    <h3>{{ item.title }}</h3>
                    <div class="card-footer">
                        <span>🏷️ {{ item.label }}</span>
                        <span class="read-more">Read More ➡️</span>
                    </div>
                </div>
                <div class="news-image-wrapper">
                    <img src="{{ item.img }}" alt="News Visual">
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
    all_news = get_optimized_news()
    response = make_response(render_template_string(HTML_TEMPLATE, news=all_news))
    
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
