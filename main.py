from flask import Flask, render_template_string, request, redirect, url_for, make_response
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "gnews_platform.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS publishers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            verified INTEGER DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            body TEXT,
            category TEXT,
            source_name TEXT,
            bg_gradient TEXT
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM publishers")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO publishers (name) VALUES (?)", [
            ("Arabian Business",), ("Tech Innovators",), ("Global Health Journal",), ("Apex Sports",), ("Capital Investment Group",)
        ])
        
        cursor.executemany("INSERT INTO reels (title, body, category, source_name, bg_gradient) VALUES (?, ?, ?, ?, ?)", [
            ("Saudi Arabia unveils $2.3bn project pipeline as healthcare and aviation surge", "Operational updates indicate significant ongoing growth trends in regional infrastructure development as Vision 2030 initiatives accelerate funding.", "investment", "Arabian Business", "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)"),
            ("Breakthrough Quantum Microchip Invention Released Globally", "Engineers have deployed a localized solid-state processing microchip architecture that doubles computational clock speeds while reducing draw matrices by 40%.", "invention", "Tech Innovators", "linear-gradient(135deg, #090d16 0%, #1e1b4b 100%)"),
            ("New Global Health Protocol Cuts Respiratory Recovery Windows", "Clinical trial systems confirm an optimized molecular delivery methodology reduces standard inpatient care metrics across major medical institutions.", "health", "Global Health Journal", "linear-gradient(135deg, #061e16 0%, #0f2e22 100%)"),
            ("Next-Gen Electric Supercar Shatters Nurburgring Track Records", "A dual-motor powertrain architecture clocked an unprecedented lap matrix, leveraging solid-state battery thermal arrays to sustain max peak torque output.", "cars", "Apex Sports", "linear-gradient(135deg, #1c0d02 0%, #2e1200 100%)")
        ])
        conn.commit()
    conn.close()

init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>GNews Platform</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg-color: #000000;
            --surface-color: #121216;
            --primary-color: #38bdf8;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: #2e2e38;
            --card-title-size: 1.55rem;
        }

        body.light-theme {
            --bg-color: #f1f5f9;
            --surface-color: #ffffff;
            --primary-color: #0284c7;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border-color: #cbd5e1;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; -webkit-tap-highlight-color: transparent; }
        body, html { background-color: var(--bg-color); height: 100%; width: 100%; overflow: hidden; transition: background-color 0.3s; }

        /* Permanent Header View */
        .top-app-header {
            position: fixed; top: 0; left: 0; right: 0; height: 60px;
            background-color: var(--surface-color); border-bottom: 1px solid var(--border-color);
            display: flex; align-items: center; justify-content: space-between; padding: 0 16px; z-index: 2500;
        }
        .app-logo-title { font-size: 1.25rem; font-weight: 900; color: var(--text-main); }
        
        .btn-hamburger {
            background: none; border: none; color: var(--text-main);
            font-size: 1.6rem; cursor: pointer; display: flex; align-items: center;
        }

        /* Multi-Category Scroll Bar under main header */
        .category-scroll-nav {
            position: fixed; top: 60px; left: 0; right: 0; height: 55px;
            background: linear-gradient(to bottom, rgba(0,0,0,0.9) 70%, rgba(0,0,0,0) 100%);
            display: flex; align-items: center; padding: 0 16px; gap: 10px;
            overflow-x: auto; white-space: nowrap; z-index: 2000;
        }
        body.light-theme .category-scroll-nav { background: var(--bg-color); }
        .category-scroll-nav::-webkit-scrollbar { display: none; }
        
        .nav-category-chip {
            background-color: rgba(28, 28, 34, 0.6); color: var(--text-muted);
            border: 1px solid var(--border-color); padding: 6px 16px;
            border-radius: 20px; font-size: 0.8rem; font-weight: 800; cursor: pointer;
            text-transform: uppercase; letter-spacing: 0.5px;
        }
        .nav-category-chip.active { background-color: var(--primary-color); color: #000000; border-color: var(--primary-color); }

        /* 100% Smooth Sliding Drawer Navigation Panel */
        .side-drawer {
            position: fixed; top: 0; bottom: 0; right: 0; width: 280px;
            background-color: var(--surface-color); border-left: 1px solid var(--border-color);
            z-index: 4000; display: flex; flex-direction: column; padding: 24px;
            transform: translateX(100%); transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: -10px 0 30px rgba(0,0,0,0.5);
        }
        .side-drawer.open { transform: translateX(0); }
        
        body.rtl .side-drawer { right: auto; left: 0; border-left: none; border-right: 1px solid var(--border-color); transform: translateX(-100%); }
        body.rtl .side-drawer.open { transform: translateX(0); }

        .drawer-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        .drawer-title { font-size: 1.2rem; font-weight: 900; color: var(--text-main); }
        .btn-close-drawer { background: none; border: none; color: #ef4444; font-size: 1.1rem; font-weight: 800; cursor: pointer; }

        .drawer-section { display: flex; flex-direction: column; gap: 20px; margin-bottom: 30px; border-bottom: 1px solid var(--border-color); padding-bottom: 20px; }
        .section-label { font-size: 0.75rem; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }

        /* Menu Settings rows */
        .setting-row { display: flex; justify-content: space-between; align-items: center; }
        .setting-name { font-size: 0.95rem; font-weight: 600; color: var(--text-main); }
        .btn-toggle-switch { background-color: var(--border-color); border: none; color: var(--text-main); padding: 6px 14px; border-radius: 8px; font-weight: 800; font-size: 0.8rem; cursor: pointer; }
        .btn-toggle-switch.active { background-color: var(--primary-color); color: #000; }

        /* Reel Items Structural Shell */
        .reel-container { height: 100%; width: 100%; overflow-y: scroll; scroll-snap-type: y mandatory; -webkit-overflow-scrolling: touch; padding-top: 60px; }
        .reel-container::-webkit-scrollbar { display: none; }

        .reel-card { width: 100%; height: 100%; scroll-snap-align: start; scroll-snap-stop: always; position: relative; display: flex; flex-direction: column; justify-content: flex-end; padding: 40px 24px 110px 24px; }
        .card-scrim { position: absolute; inset: 0; background: linear-gradient(to bottom, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.3) 50%, rgba(0,0,0,0.85) 100%); z-index: 1; }
        
        .reel-content { position: relative; z-index: 10; display: flex; flex-direction: column; gap: 14px; width: 85%; text-align: left; }
        body.light-theme .reel-headline { color: #ffffff; } /* Keep headlines readable against dark card gradients */
        body.light-theme .reel-snippet { color: #cbd5e1; }

        body.rtl .top-app-header { flex-direction: row-reverse; }
        body.rtl .category-scroll-nav { flex-direction: row-reverse; }
        body.rtl .action-sidebar { left: 16px; right: auto; }
        body.rtl .reel-content { width: 85%; text-align: right; }
        body.rtl .channel-row { flex-direction: row-reverse; }

        .channel-row { display: flex; align-items: center; gap: 8px; }
        .badge-live { background-color: #ef4444; color: white; font-size: 0.7rem; font-weight: 900; padding: 3px 9px; border-radius: 4px; text-transform: uppercase; }
        .badge-source { background-color: rgba(255,255,255,0.12); color: #ffffff; border: 1px solid rgba(255,255,255,0.15); font-size: 0.8rem; font-weight: 700; padding: 3px 12px; border-radius: 6px; backdrop-filter: blur(8px); }

        .reel-headline { font-size: var(--card-title-size); font-weight: 900; line-height: 1.35; color: #ffffff; text-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        .reel-snippet { font-size: 0.95rem; line-height: 1.55; color: #cbd5e1; opacity: 0.85; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }

        .action-sidebar { position: absolute; right: 16px; bottom: 120px; z-index: 20; display: flex; flex-direction: column; align-items: center; gap: 20px; }
        .action-button { background: rgba(28, 28, 34, 0.6); border: 1px solid rgba(255,255,255,0.1); width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.25rem; cursor: pointer; backdrop-filter: blur(10px); }
        .action-label { font-size: 0.68rem; color: #94a3b8; font-weight: 700; margin-top: 4px; text-align: center; }

        .story-modal { position: fixed; bottom: 0; left: 0; right: 0; height: 60%; background-color: #121216; border-radius: 24px 24px 0 0; border-top: 1px solid #2e2e38; z-index: 5000; display: none; flex-direction: column; padding: 24px; color: #ffffff; }
        .story-modal.open { display: flex; }
        .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; border-bottom: 1px solid #2e2e38; padding-bottom: 12px; }
        body.rtl .modal-header { flex-direction: row-reverse; }
        body.rtl .modal-body { text-align: right; }
        .btn-close-modal { background-color: #ef4444; color: white; border: none; padding: 6px 14px; border-radius: 20px; font-weight: 800; font-size: 0.8rem; cursor: pointer; }
        .modal-body { overflow-y: auto; display: flex; flex-direction: column; gap: 14px; }
        .modal-title { font-size: 1.3rem; font-weight: 800; line-height: 1.4; }
        .modal-text { font-size: 1.02rem; line-height: 1.65; color: #cbd5e1; text-align: justify; }
    </style>
</head>
<body>

    <!-- Top Navigation Header containing Menu icon -->
    <header class="top-app-header">
        <div class="app-logo-title">GNews</div>
        <button class="btn-hamburger" onclick="openNavDrawer()">☰</button>
    </header>

    <div class="category-scroll-nav">
        <div class="nav-category-chip active" id="chip-all" onclick="filterGlobalCategory('all', this)" data-en="🌐 All Streams" data-ar="🌐 كل الموجزات">🌐 All Streams</div>
        <div class="nav-category-chip" id="chip-investment" onclick="filterGlobalCategory('investment', this)" data-en="📈 Investment" data-ar="📈 الاستثمار">📈 Investment</div>
        <div class="nav-category-chip" id="chip-invention" onclick="filterGlobalCategory('invention', this)" data-en="💡 Invention" data-ar="💡 الابتكارات">💡 Invention</div>
        <div class="nav-category-chip" id="chip-health" onclick="filterGlobalCategory('health', this)" data-en="❤️ Health" data-ar="❤️ الصحة">❤️ Health</div>
        <div class="nav-category-chip" id="chip-cars" onclick="filterGlobalCategory('cars', this)" data-en="🚗 Cars" data-ar="🚗 السيارات">🚗 Cars</div>
        <div class="nav-category-chip" id="chip-sports" onclick="filterGlobalCategory('sports', this)" data-en="⚽ Sports" data-ar="⚽ الرياضة">⚽ Sports</div>
        <div class="nav-category-chip" id="chip-games" onclick="filterGlobalCategory('games', this)" data-en="🎮 Games" data-ar="🎮 الألعاب">🎮 Games</div>
    </div>

    <!-- Sliding Sidebar Menu Sheet Drawer Container -->
    <div id="sideDrawerMenu" class="side-drawer">
        <div class="drawer-header">
            <span class="drawer-title" data-en="Control Hub" data-ar="لوحة التحكم">Control Hub</span>
            <button class="btn-close-drawer" onclick="closeNavDrawer()">✕</button>
        </div>
        
        <div class="drawer-section">
            <span class="section-label" data-en="User Profile" data-ar="الملف الشخصي">User Profile</span>
            <div style="display:flex; align-items:center; gap:12px;">
                <span style="font-size:2rem;">👤</span>
                <div>
                    <h4 style="color:var(--text-main);" data-en="Anonymous Reader" data-ar="قارئ مجهول">Anonymous Reader</h4>
                    <p style="font-size:0.75rem; color:var(--text-muted);" data-en="Verified Client Account" data-ar="حساب موثق للمنصة">Verified Client Account</p>
                </div>
            </div>
        </div>

        <div class="drawer-section">
            <span class="section-label" data-en="System Configuration" data-ar="إعدادات النظام">System Configuration</span>
            
            <div class="setting-row" style="margin-bottom:14px;">
                <span class="setting-name" data-en="Language / اللغة" data-ar="اللغة / Language">Language / اللغة</span>
                <button class="btn-toggle-switch active" id="langBtn" onclick="toggleLanguage()">العربية</button>
            </div>

            <div class="setting-row" style="margin-bottom:14px;">
                <span class="setting-name" data-en="Light Theme" data-ar="المظهر الفاتح">Light Theme</span>
                <button class="btn-toggle-switch" id="themeToggle" onclick="toggleAppTheme()" data-en="Off" data-ar="إيقاف">Off</button>
            </div>
            
            <div class="setting-row">
                <span class="setting-name" data-en="Large Headlines" data-ar="تكبير العناوين">Large Headlines</span>
                <button class="btn-toggle-switch" id="textToggle" onclick="toggleTextScaling()" data-en="Off" data-ar="إيقاف">Off</button>
            </div>
        </div>
    </div>

    <div class="reel-container" id="newsFeed">
        {% for item in reels %}
        <div class="reel-card" style="background: {{ item[5] }};"
             data-category="{{ item[3] }}"
             data-title="{{ item[1] }}"
             data-source="{{ item[4] }}"
             data-body="{{ item[2] }}"
             onclick="openStoryDetails(this)">
            <div class="card-scrim"></div>
            
            <div class="reel-content">
                <div class="channel-row">
                    <span class="badge-live" data-en="Verified" data-ar="موثق">Verified</span>
                    <span class="badge-source">📡 {{ item[4] }}</span>
                </div>
                <h1 class="reel-headline">{{ item[1] }}</h1>
                <p class="reel-snippet">{{ item[2] }}</p>
                <div style="color: var(--primary-color); font-weight: 700; font-size: 0.82rem; text-transform: uppercase;">
                    <span data-en="Category" data-ar="الفئة">Category</span>: {{ item[3] }}
                </div>
            </div>

            <div class="action-sidebar">
                <div style="text-align: center;" onclick="event.stopPropagation(); alert('Saved directly to personal reader feed.')">
                    <button class="action-button">⚡</button>
                    <div class="action-label" data-en="Save" data-ar="حفظ">Save</div>
                </div>
                <div style="text-align: center;" onclick="event.stopPropagation(); alert('Broadcast share link copied.')">
                    <button class="action-button">🔗</button>
                    <div class="action-label" data-en="Share" data-ar="مشاركة">Share</div>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>

    <div id="storyModal" class="story-modal">
        <div class="modal-header">
            <span id="modalSourceBadge" class="badge-source" style="background-color: rgba(56,189,248,0.15); color: var(--primary-color);"></span>
            <button class="btn-close-modal" id="modalCloseBtn" onclick="closeStoryDetails()" data-en="❌ Close" data-ar="❌ إغلاق">❌ Close</button>
        </div>
        <div class="modal-body">
            <h2 id="modalTitle" class="modal-title"></h2>
            <p id="modalBodyText" class="modal-text"></p>
        </div>
    </div>

    <script>
        let currentLang = 'en';

        function openNavDrawer() { document.getElementById('sideDrawerMenu').classList.add('open'); }
        function closeNavDrawer() { document.getElementById('sideDrawerMenu').classList.remove('open'); }

        function toggleLanguage() {
            const body = document.body;
            const langBtn = document.getElementById('langBtn');
            
            if (currentLang === 'en') {
                currentLang = 'ar';
                body.classList.add('rtl');
                langBtn.innerText = 'English';
            } else {
                currentLang = 'en';
                body.classList.remove('rtl');
                langBtn.innerText = 'العربية';
            }

            document.querySelectorAll('[data-en]').forEach(el => {
                el.innerText = el.getAttribute('data-' + currentLang);
            });
        }

        function toggleAppTheme() {
            const body = document.body;
            const btn = document.getElementById('themeToggle');
            body.classList.toggle('light-theme');
            
            if(body.classList.contains('light-theme')) {
                btn.innerText = currentLang === 'en' ? 'On' : 'تشغيل';
                btn.classList.add('active');
            } else {
                btn.innerText = currentLang === 'en' ? 'Off' : 'إيقاف';
                btn.classList.remove('active');
            }
        }

        function toggleTextScaling() {
            const root = document.documentElement;
            const btn = document.getElementById('textToggle');
            
            if(btn.classList.contains('active')) {
                root.style.setProperty('--card-title-size', '1.55rem');
                btn.innerText = currentLang === 'en' ? 'Off' : 'إيقاف';
                btn.classList.remove('active');
            } else {
                root.style.setProperty('--card-title-size', '1.85rem');
                btn.innerText = currentLang === 'en' ? 'On' : 'تشغيل';
                btn.classList.add('active');
            }
        }

        function filterGlobalCategory(category, element) {
            document.querySelectorAll('.nav-category-chip').forEach(chip => chip.classList.remove('active'));
            element.classList.add('active');

            const cards = document.querySelectorAll('.reel-card');
            let firstVisibleCard = null;

            cards.forEach(card => {
                const cardCat = card.getAttribute('data-category');
                if (category === 'all' || cardCat === category) {
                    card.style.display = 'flex';
                    if (!firstVisibleCard) firstVisibleCard = card;
                } else {
                    card.style.display = 'none';
                }
            });

            if (firstVisibleCard) {
                firstVisibleCard.scrollIntoView({ behavior: 'smooth' });
            }
        }

        function openStoryDetails(cardElement) {
            document.getElementById('modalSourceBadge').innerText = "📡 " + cardElement.getAttribute('data-source');
            document.getElementById('modalTitle').innerText = cardElement.getAttribute('data-title');
            document.getElementById('modalBodyText').innerText = cardElement.getAttribute('data-body');

            const modal = document.getElementById('storyModal');
            modal.style.display = 'flex';
        }

        function closeStoryDetails() {
            document.getElementById('storyModal').style.display = 'none';
        }
    </script>
</body>
</html>
"""

CREATOR_PORTAL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GNews Agency Portal</title>
    <style>
        body { background-color: #0f172a; color: #f8fafc; font-family: sans-serif; padding: 40px; max-width: 600px; margin: 0 auto; }
        .card { background-color: #1e293b; padding: 25px; border-radius: 12px; border: 1px solid #334155; }
        h1 { color: #38bdf8; margin-bottom: 20px; }
        label { display: block; margin: 12px 0 6px; font-weight: bold; font-size: 0.9rem; }
        input, textarea, select { width: 100%; padding: 12px; background-color: #0f172a; border: 1px solid #334155; color: white; border-radius: 6px; margin-bottom: 10px; font-size: 1rem; }
        button { background-color: #38bdf8; color: #0f172a; border: none; width: 100%; padding: 14px; border-radius: 6px; font-weight: bold; font-size: 1rem; cursor: pointer; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>📡 Agency Dashboard</h1>
        <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 20px;">Authenticated Platform Broadcast Upload Terminal</p>
        <form action="/publish" method="POST">
            <label>Select Your Certified News Agency</label>
            <select name="source_name">
                {% for agency in agencies %}
                <option value="{{ agency[1] }}">{{ agency[1] }}</option>
                {% endfor %}
            </select>
            
            <label>Broadcast Title Headline</label>
            <input type="text" name="title" placeholder="e.g., Global Market Shifts..." required>
            
            <label>News Content Scope (Full Story)</label>
            <textarea name="body" rows="5" placeholder="Write full context here..." required></textarea>
            
            <label>Content Category Target</label>
            <select name="category">
                <option value="investment">Investment / الاستثمار</option>
                <option value="invention">Invention / الابتكارات</option>
                <option value="health">Health / الصحة</option>
                <option value="cars">Cars / السيارات</option>
                <option value="sports">Sports / الرياضة</option>
                <option value="games">Games / الألعاب</option>
            </select>
            
            <button type="submit">🚀 Deploy Live Broadcast Reel</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, body, category, source_name, bg_gradient FROM reels ORDER BY id DESC")
    all_reels = cursor.fetchall()
    conn.close()
    
    response = make_response(render_template_string(HTML_TEMPLATE, reels=all_reels))
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/agency-portal')
def agency_portal():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM publishers")
    agencies = cursor.fetchall()
    conn.close()
    return render_template_string(CREATOR_PORTAL_TEMPLATE, agencies=agencies)

@app.route('/publish', methods=['POST'])
def publish_story():
    title = request.form.get('title')
    body = request.form.get('body')
    category = request.form.get('category')
    source_name = request.form.get('source_name')
    
    color_schemes = {
        "investment": "linear-gradient(135deg, #111827 0%, #06b6d4 100%)",
        "invention": "linear-gradient(135deg, #0f172a 0%, #4f46e5 100%)",
        "health": "linear-gradient(135deg, #022c22 0%, #0d9488 100%)",
        "cars": "linear-gradient(135deg, #1e1b4b 0%, #b45309 100%)",
        "sports": "linear-gradient(135deg, #0f172a 0%, #1d4ed8 100%)",
        "games": "linear-gradient(135deg, #311042 0%, #701a75 100%)"
    }
    bg_gradient = color_schemes.get(category, "linear-gradient(135deg, #000000 0%, #1c1c22 100%)")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reels (title, body, category, source_name, bg_gradient) VALUES (?, ?, ?, ?, ?)",
                   (title, body, category, source_name, bg_gradient))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
