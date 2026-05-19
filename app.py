# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

# ==================== MA'LUMOTLAR ====================
PROJECTS = [
    {
        "id": 1,
        "title": "E-Commerce Platform",
        "description": "To‘liq funksional online do‘kon. Flask backend, SQLite, admin panel.",
        "tech": ["Python", "Flask", "SQLite", "HTML/CSS"],
        "icon": "🛒",
        "live_url": "#",
        "code_url": "#"
    },
    {
        "id": 2,
        "title": "Weather Dashboard",
        "description": "OpenWeather API bilan real-time ob-havo. Interaktiv va responsive.",
        "tech": ["JavaScript", "API", "CSS Grid"],
        "icon": "☁️",
        "live_url": "#",
        "code_url": "#"
    },
    {
        "id": 3,
        "title": "Task Manager (Kanban)",
        "description": "Drag & drop, localStorage, kategoriyalar. Vazifalarni boshqarish.",
        "tech": ["JS", "Drag & Drop", "LocalStorage"],
        "icon": "📝",
        "live_url": "#",
        "code_url": "#"
    },
    {
        "id": 4,
        "title": "Python Web Scraper",
        "description": "BeautifulSoup + Selenium. Ma’lumotlarni CSV/JSON ga saqlaydi.",
        "tech": ["Python", "BeautifulSoup", "Selenium"],
        "icon": "🤖",
        "live_url": "#",
        "code_url": "#"
    }
]

MESSAGES = []  # Vaqtinchalik xotira (real loyihada DB ishlatiladi)

STATS = {
    "projects": len(PROJECTS),
    "experience_months": 20,
    "technologies": 9
}

# ==================== API ENDPOINTS ====================
@app.route('/')
def serve_index():
    """Frontend index.html ni ko‘rsatadi"""
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """CSS, JS va boshqa statik fayllarni qaytaradi"""
    return send_from_directory('frontend', path)

@app.route('/api/health')
def health():
    """Backend ishlayotganligini tekshirish"""
    return jsonify({"status": "online", "timestamp": datetime.now().isoformat()})

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Barcha loyihalarni qaytaradi"""
    return jsonify(PROJECTS)

@app.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """ID bo‘yicha bitta loyiha"""
    project = next((p for p in PROJECTS if p["id"] == project_id), None)
    if project:
        return jsonify(project)
    return jsonify({"error": "Project not found"}), 404

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Statistikani qaytaradi"""
    return jsonify(STATS)

@app.route('/api/contact', methods=['POST'])
def contact():
    """Kontakt formadan kelgan xabarni qabul qiladi"""
    data = request.get_json()
    if not data or not data.get('name') or not data.get('email') or not data.get('message'):
        return jsonify({"success": False, "message": "Barcha maydonlarni to‘ldiring"}), 400
    
    message = {
        "id": len(MESSAGES) + 1,
        "name": data['name'],
        "email": data['email'],
        "message": data['message'],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    MESSAGES.append(message)
    
    # Konsolga chiqarish (Railway loglarida ko‘rinadi)
    print(f"\n📨 New message from {message['name']} ({message['email']}):")
    print(f"   {message['message']}\n")
    
    return jsonify({"success": True, "message": "Xabar qabul qilindi! Tez orada javob beramiz."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)