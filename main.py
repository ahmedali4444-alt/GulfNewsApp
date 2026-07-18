from flask import Flask, render_template_string, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_saudi_auto_news():
    articles = []
    try:
        url = "https://saudiauto.com.sa/%d8%a3%d8%ae%d8%a1%d8%a7%d8%b1-%d8%a7%d9%84%d8%b3%d9%8a%d8%a7%d8%b1%d8%a7%d8%aa/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            posts = soup.find_all('div', class_='post-inner')  # Adjusted for common themes
            if not posts:
                posts = soup.find_all('article')
                
            for post in posts[:6]:
                title_tag = post.find('h3') or post.find('h2')
                desc_tag = post.find('p')
                
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    desc = desc_tag.get_text(strip=True) if desc_tag else "اضغط على قراءة المزيد لمتابعة تفاصيل الخبر بالكامل عبر المصدر."
                    articles.append({
                        "category": "cars",
                        "title": title,
                        "desc": desc,
                        "time": "سيارات"
                    })
    except Exception as e:
        print(f"Error scraping cars: {e}")
        
    # Fallback if scraping gets blocked
    if not articles:
        articles = [
            {"category": "cars", "title": "شركة ford تستدعي 288 ألف إكسبلورر في أمريكا.. ماذا عن المملكة؟", "desc": "سعودي أوتو أعلنت شركة فورد العالمية رسمياً عن استدعاء ضخم يشمل مركبات إكسبلورر...", "time": "سيارات"},
            {"category": "cars", "title": "لينكولن فاخرة للطرق الوعرة في 2029 تحدياً لديفندر ومرسيدس G ولكزس GX", "desc": "تحدياً لسيارات الدفع الرباعي الفاخرة، تم الإعلان عن مشروع لينكولن الجديد...", "time": "سيارات"}
        ]
    return articles

def get_sports_news():
    # Dynamic sports news fallback
    return [
        {
            "category": "sports",
            "title": "متابعة صفقات الأندية الخليجية في سوق الانتقالات الصيفي",
            "desc": "تستمر الأندية في تعزيز صفوفها بمجموعة من خيارات اللاعبين النخبة استعداداً للمواجهات الكروية القادمة.",
            "time": "رياضة"
        },
        {
            "category": "sports",
            "title": "فيصل القباني يتصدر اليوم الأول من الجولة 2 لبطولة صعود الهضبة",
            "desc": "انطلقت منافسات الجولة الثانية وسط حضور جماهيري كبير وأجواء تنافسية عالية بين المتسابقين.",
            "time": "رياضة"
        }
    ]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>رادار أخبار الخليج</title>
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
            padding-top: 75px;
            padding-bottom: 85px;
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

        .nav-btn {
            background: none;
            border: none;
            color: var(--text-main);
            font-size: 1.3rem;
            cursor: pointer;
            visibility: hidden; /* Controlled via JS */
        }

        .lang-btn {
            background: none;
            border: none;
            color: var(--text-main);
            font-size: 1.3rem;
            cursor: pointer;
        }

        .app-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--text-main);
        }

        /* --- HORIZONTAL CATEGORY CHIPS --- */
        .category-container {
            padding: 10px 20px 20px 20px;
            display: flex;
            gap: 10px;
            overflow-x: auto;
            white-space: nowrap;
        }
        .category-container::-webkit-scrollbar { display: none; }

        .chip {
            background-color: var(--surface-color);
            color: var(--text-muted);
            padding: 6px 20px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            border: 1px solid var(--border-color);
            cursor: pointer;
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
            padding: 18px;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }

        .news-card h3 {
            font-size: 1.1rem;
            line-height: 1.5;
            color: var(--primary-color);
            margin-bottom: 10px;
        }

        .news-card p {
            font-size: 0.9rem;
            color: var(--text-muted);
            line-height: 1.6;
            margin-bottom: 14px;
        }

        .card-footer {
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: var(--text-muted);
        }

        .placeholder-view {
            text-align: center;
            padding: 60px 20px;
        }
        .placeholder-view h2 { color: var(--text-main); margin-bottom: 12px; }
        .placeholder-view p { color: var(--text-muted); }

        /* --- STICKY BOTTOM NAVIGATION DOCK --- */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 75px;
            background-color: #161619;
            border-top: 1px solid var(--border-color);
            display: flex;
            justify-content: space-around;
            align-items: center;
            z-index: 1000;
            padding-bottom: env(safe-area-inset-bottom);
        }

        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: var(--text-muted);
            background: none;
            border: none;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            width: 33%;
            gap: 4px;
        }

        .nav-item .icon { font-size: 1.4rem; }
        .nav-item.active { color: var(--primary-color); }
    </style>
</head>
<body>

    <!-- TOP HEADER -->
    <header class="top-header">
        <button class="nav-btn" id="backBtn" onclick="goToHome()">⬅️</button>
        <div class="app-title" id="mainHeaderTitle">رادار أخبار الخليج</div>
        <button class="lang-btn" onclick="alert('تغيير اللغة / Settings Language')">🌐</button>
    </header>

    <!-- SCREEN 1: HOME (NEWS CONTENT) -->
    <main id="homeScreen" class="screen active">
        <div class="category-container">
            <div class="chip active" onclick="filterCategory('all', this)">الكل</div>
            <div class="chip" onclick="filterCategory('cars', this)">سيارات</div>
            <div class="chip" onclick="filterCategory('sports', this)">رياضة</div>
        </div>

        <div class="news-feed" id="newsFeed">
            {% for item in news %}
            <div class="news-card" data-category="{{ item.category }}">
                <h3>{{ item.title }}</h3>
                <p>{{ item.desc }}</p>
                <div class="card-footer">
                    <span>🏷️ {{ item.time }}</span>
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
            <p>مرحباً بك في لوحة تحكم حسابك الشخصي لرادار الخليج.</p>
        </div>
    </section>

    <!-- SCREEN 3: SETTINGS VIEW -->
    <section id="settingsScreen" class="screen">
        <div class="placeholder-view">
            <h2>⚙️ الإعدادات العامة</h2>
            <p>تخصيص وضع القراءة، الإشعارات الفورية، ومزامنة المصادر الإخبارية.</p>
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

    <script>
        function filterCategory(category, element) {
            document.querySelectorAll('.chip').forEach(chip => chip.classList.remove('active'));
            element.classList.add('active');

            const cards = document.querySelectorAll('.news-card');
            cards.forEach(card => {
                if (category === 'all' || card.getAttribute('data-category') === category) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
            goToHome();
        }

        function switchTab(screenName) {
            const titles = { 'home': 'رادار أخبار الخليج', 'profile': 'الملف الشخصي', 'settings': 'الإعدادات والمظهر' };
            document.getElementById('mainHeaderTitle').innerText = titles[screenName];

            document.querySelectorAll('.screen').forEach(scr => scr.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(tab => tab.classList.remove('active'));

            document.getElementById(screenName + 'Screen').classList.add('active');
            document.getElementById('tab-' + screenName).classList.add('active');

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
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    # Gather live automotive news + sports layouts
    all_news = get_saudi_auto_news() + get_sports_news()
    return render_template_string(HTML_TEMPLATE, news=all_news)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
