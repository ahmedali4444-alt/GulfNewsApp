from flask import Flask, render_template_string, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Sample/Scraped Data Structure
def get_gulf_news():
    # This simulates your scraper output categorized cleanly
    articles = [
        {
            "id": 1,
            "category": "cars",
            "title": "شركة فورد تستدعي 288 ألف إكسبلورر في أمريكا.. ماذا عن المملكة؟",
            "desc": "سعودي أوتو أعلنت شركة فورد العالمية رسمياً عن استدعاء ضخم يشمل أكثر من 288 ألف سيارة من طراز إكسبلورر...",
            "time": "قبل ساعتين"
        },
        {
            "id": 2,
            "category": "cars",
            "title": "لينكولن فاخرة للطرق الوعرة في 2029 تحدياً لديفندر ومرسيدس G ولكزس GX",
            "desc": "تحدياً لسيارات الدفع الرباعي الفاخرة، تم الإعلان عن مشروع لينكولن الجديد لتقديم مركبة متطورة ومخصصة للمهام الصعبة...",
            "time": "قبل ٤ ساعات"
        },
        {
            "id": 3,
            "category": "sports",
            "title": "متابعة صفقات الأندية الخليجية في سوق الانتقالات الصيفي",
            "desc": "تستمر الأندية في تعزيز صفوفها بمجموعة من خيارات اللاعبين النخبة استعداداً للمواجهات الكروية القادمة في الموسم الجديد...",
            "time": "قبل ٥ ساعات"
        }
    ]
    return articles

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>رادار أخبار الخليج</title>
    <!-- Google Fonts for Premium Arabic Typography -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg-color: #121214;
            --surface-color: #1a1a1e;
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
            padding-top: 70px; /* Space for top header */
            padding-bottom: 80px; /* Space for bottom nav */
            overflow-x: hidden;
        }

        /* --- TOP HEADER BAR --- */
        .top-header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 65px;
            background-color: rgba(26, 26, 30, 0.95);
            backdrop-filter: blur(10px);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            border-bottom: 1px solid var(--border-color);
            z-index: 1000;
        }

        .header-left, .header-right {
            display: flex;
            align-items: center;
            gap: 15px;
            width: 20%;
        }

        .header-right { justify-content: flex-start; }
        .header-left { justify-content: flex-end; }

        .nav-btn {
            background: none;
            border: none;
            color: var(--text-main);
            font-size: 1.3rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: color 0.2s;
        }
        
        .nav-btn:active { color: var(--primary-color); }

        .app-title {
            font-size: 1.2rem;
            font-weight: 700;
            text-align: center;
            flex-grow: 1;
            color: var(--text-main);
        }

        /* --- HORIZONTAL CATEGORY CHIPS --- */
        .category-container {
            padding: 15px 20px;
            display: flex;
            gap: 10px;
            overflow-x: auto;
            white-space: nowrap;
            scrollbar-width: none; /* Hide scrollbar Firefox */
        }
        .category-container::-webkit-scrollbar { display: none; } /* Hide scrollbar Chrome/Safari */

        .chip {
            background-color: var(--surface-color);
            color: var(--text-muted);
            padding: 6px 18px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            border: 1px solid var(--border-color);
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .chip.active {
            background-color: var(--primary-color);
            color: #000;
            border-color: var(--primary-color);
            box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2);
        }

        /* --- MAIN CONTENT SCREENS --- */
        .screen { display: none; padding: 0 20px; }
        .screen.active { display: block; }

        /* --- NEWS CARDS STYLING --- */
        .news-feed {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .news-card {
            background-color: var(--surface-color);
            border-radius: 14px;
            padding: 16px;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 6px rgba(0,0,0,0.15);
            cursor: pointer;
        }

        .news-card h3 {
            font-size: 1.05rem;
            line-height: 1.5;
            color: var(--primary-color);
            margin-bottom: 8px;
        }

        .news-card p {
            font-size: 0.9rem;
            color: var(--text-muted);
            line-height: 1.6;
            margin-bottom: 12px;
        }

        .card-footer {
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            color: var(--text-muted);
        }

        /* --- PLACEHOLDER UTILITY VIEWS (Profile / Settings) --- */
        .placeholder-view {
            text-align: center;
            padding: 50px 20px;
            color: var(--text-muted);
        }
        .placeholder-view h2 { color: var(--text-main); margin-bottom: 10px; }

        /* --- STICKY BOTTOM NAVIGATION DOCK --- */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 70px;
            background-color: #161619;
            border-top: 1px solid var(--border-color);
            display: flex;
            justify-content: space-around;
            align-items: center;
            z-index: 1000;
            padding-bottom: env(safe-area-inset-bottom); /* iOS/Android gesture bar support */
        }

        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: var(--text-muted);
            background: none;
            border: none;
            font-size: 0.75rem;
            font-weight: 600;
            cursor: pointer;
            width: 25%;
            height: 100%;
            gap: 4px;
        }

        .nav-item .icon { font-size: 1.35rem; }
        .nav-item.active { color: var(--primary-color); }
    </style>
</head>
<body>

    <!-- TOP HEADER -->
    <header class="top-header">
        <div class="header-right">
            <button class="nav-btn" id="backBtn" onclick="goToHome()">⬅️</button>
        </div>
        <div class="app-title" id="mainHeaderTitle">رادار أخبار الخليج</div>
        <div class="header-left">
            <button class="nav-btn" onclick="alert('تغيير اللغة / Language Switcher')">🌐</button>
        </div>
    </header>

    <!-- SCREEN 1: NEWS CONTENT (HOME) -->
    <main id="homeScreen" class="screen active">
        <!-- Horizontal Filter Bar -->
        <div class="category-container">
            <div class="chip active" onclick="filterCategory('all', this)">الكل</div>
            <div class="chip" onclick="filterCategory('cars', this)">سيارات</div>
            <div class="chip" onclick="filterCategory('sports', this)">رياضة</div>
        </div>

        <!-- Dynamic Feed -->
        <div class="news-feed" id="newsFeed">
            {% for item in news %}
            <div class="news-card" data-category="{{ item.category }}" onclick="alert('فتح تفاصيل الخبر...')">
                <h3>{{ item.title }}</h3>
                <p>{{ item.desc }}</p>
                <div class="card-footer">
                    <span>⏱️ {{ item.time }}</span>
                    <span>🔗 قراءة المزيد</span>
                </div>
            </div>
            {% endfor %}
        </div>
    </main>

    <!-- SCREEN 2: PROFILE VIEW -->
    <section id="profileScreen" class="screen">
        <div class="placeholder-view">
            <h2>👤 الملف الشخصي</h2>
            <p>مرحباً بك في لوحة تحكم حسابك الشخصي.</p>
        </div>
    </section>

    <!-- SCREEN 3: SETTINGS VIEW -->
    <section id="settingsScreen" class="screen">
        <div class="placeholder-view">
            <h2>⚙️ الإعدادات العامة</h2>
            <p>تخصيص وضع القراءة، الإشعارات الفورية، وتفضيلات المحتوى.</p>
        </div>
    </section>

    <!-- BOTTOM FIXED NAVIGATION -->
    <nav class="bottom-nav">
        <button class="nav-item active" id="tab-home" onclick="switchTab('home')">
            <span class="icon">🏠</span>
            <span>الرئيسية</span>
        </button>
        <button class="nav-item" id="tab-profile" onclick="switchTab('profile')">
            <span class="icon">👤</span>
            <span>حسابي</span>
        </button>
        <button class="nav-item" id="tab-settings" onclick="switchTab('settings')">
            <span class="icon">⚙️</span>
            <span>الإعدادات</span>
        </button>
    </nav>

    <!-- INTERACTIVE APP CONTROLLER SCRIPT -->
    <script>
        // Category Filter Logic (Fixes the non-responsive buttons)
        function filterCategory(category, element) {
            // Update active chip styling
            document.querySelectorAll('.chip').forEach(chip => chip.classList.remove('active'));
            element.classList.add('active');

            // Show/Hide cards natively
            const cards = document.querySelectorAll('.news-card');
            cards.forEach(card => {
                if (category === 'all' || card.getAttribute('data-category') === category) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
            
            // Auto return to home layout if using navigation filtering
            goToHome();
        }

        // Tab Navigation Controller (Fixes Profile & Settings visibility)
        function switchTab(screenName) {
            // Update App header title contexts cleanly
            const titles = { 'home': 'رادار أخبار الخليج', 'profile': 'الملف الشخصي', 'settings': 'الإعدادات والمظهر' };
            document.getElementById('mainHeaderTitle').innerText = titles[screenName];

            // Toggle active content layouts
            document.querySelectorAll('.screen').forEach(scr => scr.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(tab => tab.classList.remove('active'));

            document.getElementById(screenName + 'Screen').classList.add('active');
            document.getElementById('tab-' + screenName).classList.add('active');

            // Manage visible state of the custom back button
            const backBtn = document.getElementById('backBtn');
            if (screenName === 'home') {
                backBtn.style.visibility = 'hidden';
            } else {
                backBtn.style.visibility = 'visible';
            }
        }

        function goToHome() {
            switchTab('home');
        }

        // Initialize view states on bootup
        document.addEventListener("DOMContentLoaded", function() {
            document.getElementById('backBtn').style.visibility = 'hidden';
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    news_data = get_gulf_news()
    return render_template_string(HTML_TEMPLATE, news=news_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
