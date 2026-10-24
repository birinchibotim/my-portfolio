# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
from email.message import EmailMessage
from email.utils import formataddr
import json
import os
import re
import smtplib
import ssl
import threading
import urllib.request

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

# ==================== MA'LUMOTLAR ====================
PROJECTS = [
    {
        "id": 1,
        "title": "E-Commerce Platform",
        "description": "ToвЂliq funksional online doвЂkon. Flask backend, SQLite, admin panel.",
        "tech": ["Python", "Flask", "SQLite", "HTML/CSS"],
        "icon": "рџ›’",
        "live_url": "#",
        "code_url": "#"
    },
    {
        "id": 2,
        "title": "Weather Dashboard",
        "description": "OpenWeather API bilan real-time ob-havo. Interaktiv va responsive.",
        "tech": ["JavaScript", "API", "CSS Grid"],
        "icon": "вЃпёЏ",
        "live_url": "#",
        "code_url": "#"
    },
    {
        "id": 3,
        "title": "Task Manager (Kanban)",
        "description": "Drag & drop, localStorage, kategoriyalar. Vazifalarni boshqarish.",
        "tech": ["JS", "Drag & Drop", "LocalStorage"],
        "icon": "рџ“ќ",
        "live_url": "#",
        "code_url": "#"
    },
    {
        "id": 4,
        "title": "Python Web Scraper",
        "description": "BeautifulSoup + Selenium. MaвЂ™lumotlarni CSV/JSON ga saqlaydi.",
        "tech": ["Python", "BeautifulSoup", "Selenium"],
        "icon": "рџ¤–",
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


# ==================== EMAIL SOZLAMALARI ====================
# Maxfiy ma'lumotlar kodda emas, muhit o'zgaruvchilarida (Environment Variables) saqlanadi.
OWNER_EMAIL = os.environ.get("OWNER_EMAIL", "ilhomsubanqulov564@gmail.com")
SMTP_USER = os.environ.get("SMTP_USER", OWNER_EMAIL)      # Gmail manzilingiz
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")       # Gmail "App Password" (16 ta belgi)
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 465))
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")     # ixtiyoriy (SMTP bloklangan hostinglar uchun)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _clean(text, limit):
    """Sarlavhalarga (header) begona qator qo'shishni (injection) oldini oladi."""
    return re.sub(r"[\r\n]+", " ", str(text)).strip()[:limit]


def _send_via_smtp(subject, body, reply_to):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr(("Portfolio sayt", SMTP_USER))
    msg["To"] = OWNER_EMAIL
    msg["Reply-To"] = reply_to          # "Javob berish" bossangiz, to'g'ridan-to'g'ri mijozga ketadi
    msg.set_content(body)
    ctx = ssl.create_default_context()
    if SMTP_PORT == 465:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx, timeout=20) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
    else:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            server.starttls(context=ctx)
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)


def _send_via_resend(subject, body, reply_to):
    payload = json.dumps({
        "from": "Portfolio <onboarding@resend.dev>",
        "to": [OWNER_EMAIL],
        "reply_to": reply_to,
        "subject": subject,
        "text": body,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.resend.com/emails", data=payload, method="POST",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
    )
    urllib.request.urlopen(req, timeout=20).read()


def send_notification(message):
    """Yangi xabar kelganda egasining emailiga yuboradi (fon rejimida, sayt qotib qolmaydi)."""
    subject = f"рџ“Ё Portfolio: {message['name']} dan yangi xabar"
    body = (
        f"Saytingiz orqali yangi xabar keldi.\n\n"
        f"Ism:    {message['name']}\n"
        f"Email:  {message['email']}\n"
        f"Sana:   {message['date']}\n\n"
        f"Xabar:\n{message['message']}\n"
    )

    def worker():
        try:
            if SMTP_PASSWORD:
                _send_via_smtp(subject, body, message["email"])
            elif RESEND_API_KEY:
                _send_via_resend(subject, body, message["email"])
            else:
                print("вљ пёЏ Email yuborilmadi: SMTP_PASSWORD yoki RESEND_API_KEY sozlanmagan")
                return
            print(f"вњ… Email yuborildi -> {OWNER_EMAIL}")
        except Exception as e:
            print(f"вќЊ Email yuborishda xatolik: {e}")

    threading.Thread(target=worker, daemon=True).start()

# ==================== API ENDPOINTS ====================
@app.route('/')
def serve_index():
    """Frontend index.html ni koвЂrsatadi"""
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
    """ID boвЂyicha bitta loyiha"""
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
    data = request.get_json(silent=True)
    if not data or not data.get('name') or not data.get('email') or not data.get('message'):
        return jsonify({"success": False, "message": "Barcha maydonlarni toвЂldiring"}), 400

    email = _clean(data['email'], 200)
    if not EMAIL_RE.match(email):
        return jsonify({"success": False, "message": "Email manzil notoвЂgвЂri"}), 400

    message = {
        "id": len(MESSAGES) + 1,
        "name": _clean(data['name'], 100),
        "email": email,
        "message": str(data['message']).strip()[:5000],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    MESSAGES.append(message)

    # Konsolga chiqarish (Railway loglarida koвЂrinadi)
    print(f"\nрџ“Ё New message from {message['name']} ({message['email']}):")
    print(f"   {message['message']}\n")

    # Emailga yuborish
    send_notification(message)

    return jsonify({"success": True, "message": "Xabar qabul qilindi! Tez orada javob beramiz."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)