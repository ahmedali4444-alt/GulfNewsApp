from flask import Flask, render_template_string, request, redirect, url_for, make_response
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "gnews_platform.db"

# Database Configuration and Seed Logic
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Create Publishers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS publishers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            verified INTEGER DEFAULT 1
        )
    ''')
    
    # 2. Create News Reels Table supporting all custom categories
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
    
    # Seed Initial Channels if empty
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

# Premium Dynamic UI Icons
ICON_MAP = {
    "all": "🌐", "health": "❤️", "investment": "📈", "invention": "💡", 
    "cars": "🚗", "sports": "⚽", "games": "🎮"
}

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
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; -webkit-tap-highlight-color: transparent; }
        body, html { background-color: #000000; height: 100%; width: 100%; overflow: hidden; }

        /* Multi-Category Floating Navigation Header Bar */
        .category-scroll-nav {
            position: fixed; top: 0; left: 0; right: 0; height: 65px;
            background: linear-gradient(to bottom, rgba(0,0,0,0.9) 70%, rgba(0,0,0,0) 100%);
            display: flex; align-items: center; padding: 0 16px; gap: 10px;
            overflow-x: auto; white-space: nowrap; z-index: 2000;
        }
        .category-scroll-nav::-webkit-scrollbar { display: none; }
        
        .nav-category-chip {
            background-color: rgba(28, 28, 34, 0.6); color: #94a3b8;
            border: 1px solid rgba(255,255,255,0.1); padding: 6px 16px;
            border-radius: 20px; font-size: 0.8rem; font-weight: 800; cursor: pointer;
            text-transform: uppercase; letter-spacing: 0.5px;
        }
        .nav-category-chip.active { background-color: #38bdf8; color: #000000; border-color: #38bdf8; }

        .reel-container { height: 100%; width: 100%; overflow-y: scroll; scroll-snap-type: y mandatory; -webkit-overflow-scrolling: touch; }
        .reel-container::-webkit-scrollbar { display: none; }

        .reel-card {
            width: 100%; height: 100%; scroll-snap-align: start; scroll-snap-stop: always;
            position: relative; display: flex; flex-direction: column; justify-content: flex-end;
            padding: 40px 24px 110px 24px;
        }

        .card-scrim { position: absolute; inset: 0; background: linear-gradient(to bottom, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.3) 50%, rgba(0,0,0,0.85) 100%); z-index: 1; }
        .reel-content { position: relative; z-index: 10; display: flex; flex-direction: column; gap: 14px; width: 85%; }
        
        .channel-row { display: flex; align-items: center; gap: 8px; }
        .badge-live { background-color: #ef4444; color: white; font-size: 0.7rem; font-weight: 900; padding: 3px 9px; border-radius: 4px; text-transform: uppercase; }
        .badge-source { background-color: rgba(255,255,255,0.12); color: #ffffff; border: 1px solid rgba(255,255,255,0.15); font-size: 0.8rem; font-weight: 700; padding: 3px 12px; border-radius: 6px; backdrop-filter: blur(8px); }

        .reel-headline { font-size: 1.55rem; font-weight: 900; line-height: 1.35; color: #ffffff; text-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        .reel-snippet { font-size: 0.95rem; line-height: 1.55; color: #cbd5e1; opacity: 0.85; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }

        .action-sidebar { position: absolute; right: 16px; bottom: 120px; z-index: 20; display: flex; flex-direction: column; align-items: center; gap: 20px; }
        .action-button { background: rgba(28, 28, 34, 0.6); border: 1px solid rgba(255,255,255,0.1); width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.25rem; cursor: pointer; backdrop-filter: blur(10px); }
        .action-label { font-size: 0.68rem; color: #94a3b8; font-weight: 700; margin-top: 4px; text-align: center; }

        /* Dynamic Detail Modal Sheet */
        .story-modal { position: fixed; bottom: 0; left: 0; right: 0; height: 60%; background-color: #121216; border-radius: 24px 24px 0 0; border-top: 1px solid #2e2e38; z-index: 5000; display: none; flex-direction: column; padding: 24px; color: #ffffff; }
        .story-modal.open { display: flex; }
        .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; border-bottom: 1px solid #2e2e38; padding-bottom: 12px; }
        .btn-close-modal { background-color: #ef4444; color: white; border: none; padding: 6px 14px; border-radius: 20px; font-weight: 800; font-size: 0.8rem; cursor: pointer; }
        .modal-body { overflow-y: auto; display: flex; flex-direction: column; gap: 14px; }
        .modal-title { font-size: 1.3rem; font-weight: 800; line-height: 1.4; }
        .modal-text { font-size: 1.02rem; line-height: 1.65; color: #cbd5e1; text-align: justify; }
    </style>
</head>
<body>

    <!-- Scrollable Global Category Switcher Ribbon -->
    <div class="category-scroll-nav">
        <div class="nav-category-chip active" onclick="filterGlobalCategory('all', this)">🌐 All Streams</div>
        <div class="nav-category-chip" onclick="filterGlobalCategory('investment', this)">📈 Investment</div>
        <div class="nav-category-chip" onclick="filterGlobalCategory('invention', this)">💡 Invention</div>
        <div class="nav-category-chip" onclick="filterGlobalCategory('health', this)">❤️ Health</div>
        <div class="nav-category-chip" onclick="filterGlobalCategory('cars', this)">🚗 Cars</div>
        <div class="nav-category-chip" onclick="filterGlobalCategory('sports', this)">⚽ Sports</div>
        <div class="nav-category-chip" onclick="filterGlobalCategory('games', this)">🎮 Games</div>
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
                    <span class="badge-live">Verified</span>
                    <span class="badge-source">📡 {{ item[4] }}</span>
                </div>
                <h1 class="reel-headline">{{ item[1] }}</h1>
                <p class="reel-snippet">{{ item[2] }}</p>
                <div style="color: #38bdf8; font-weight: 700; font-size: 0.82rem; text-transform: uppercase;">
                    Category: {{ item[3] }}
                </div>
            </div>

            <div class="action-sidebar">
                <div style="text-align: center;" onclick="event.stopPropagation(); alert('Saved directly to personal reader feed.')">
                    <button class="action-button">⚡</button>
                    <div class="action-label">Save</div>
                </div>
                <div style="text-align: center;" onclick="event.stopPropagation(); alert('Broadcast share link copied.')">
                    <button class="action-button">🔗</button>
                    <div class="action-label">Share</div>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>

    <div id="storyModal" class="story-modal">
        <div class="modal-header">
            <span id="modalSourceBadge" class="badge-source" style="background-color: rgba(56,189,248,0.15); color: #38bdf8;"></span>
            <button class="btn-close-modal" onclick="closeStoryDetails()">❌ Close</button>
        </div>
        <div class="modal-body">
            <h2 id="modalTitle" class="modal-title"></h2>
            <p id="modalBodyText" class="modal-text"></p>
        </div>
    </div>

    <script>
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
                <option value="investment">Investment</option>
                <option value="invention">Invention</option>
                <option value="health">Health</option>
                <option value="cars">Cars</option>
                <option value="sports">Sports</option>
                <option value="games">Games</option>
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

# Hidden Publisher route to test content creation
@app.route('/agency-portal')
def agency_portal():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM publishers")
    agencies = cursor.fetchall()
    conn.close()
    return render_template_string(CREATOR_PORTAL_TEMPLATE, agencies=agencies)

# FIXED: Changed 'method' argument to plural 'methods'
@app.route('/publish', methods=['POST'])
def publish_story():
    title = request.form.get('title')
    body = request.form.get('body')
    category = request.form.get('category')
    source_name = request.form.get('source_name')
    
    # Generate unique premium colors dynamically based on category types
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
