# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

# ==================== SOZLAMALAR ====================
# Render/Railway'da Environment Variables orqali beriladi
EMAIL_SENDER   = os.environ.get('EMAIL_SENDER', 'ilhomsubanqulov564@gmail.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')          # Gmail App Password
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER', 'ilhomsubanqulov564@gmail.com')
SMTP_HOST      = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT      = int(os.environ.get('SMTP_PORT', 465))         # 465 = SSL

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

MESSAGES = []

STATS = {
    "projects": len(PROJECTS),
    "experience_months": 20,
    "technologies": 9
}

# ==================== EMAIL YUBORISH ====================
def send_email_notification(message: dict) -> bool:
    """
    Kontakt formasidan kelgan xabarni EMAIL_RECEIVER ga yuboradi.
    Muvaffaqiyatli bo'lsa True, aks holda False qaytaradi.
    """
    if not EMAIL_PASSWORD:
        print("⚠️  EMAIL_PASSWORD o'rnatilmagan — email yuborilmadi.")
        return False

    try:
        # --- Foydalanuvchiga javob xati (Reply-To) ---
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"📨 Yangi xabar: {message['name']} — Portfolio"
        msg['From']    = formataddr(("Portfolio Bot", EMAIL_SENDER))
        msg['To']      = EMAIL_RECEIVER
        # Javob bersangiz to'g'ridan-to'g'ri foydalanuvchiga ketadi:
        msg['Reply-To'] = formataddr((message['name'], message['email']))

        # --- Matnli versiya ---
        text_body = f"""Yangi xabar keldi!

👤 Ism:    {message['name']}
📧 Email:  {message['email']}
🕒 Vaqt:   {message['date']}

💬 Xabar:
{message['message']}

---
Bu xabar DevPortfolio saytidagi kontakt formasi orqali yuborilgan.
"""

        # --- HTML versiya (chiroyliroq) ---
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background:#f4f4f4; padding:20px;">
          <div style="max-width:600px; margin:auto; background:#fff; border-radius:12px;
                      padding:24px; border:1px solid #e5e7eb;">
            <h2 style="color:#3b82f6; margin-top:0;">📨 Yangi xabar keldi</h2>
            <table style="width:100%; border-collapse:collapse;">
              <tr><td style="padding:8px 0; color:#6b7280;">👤 Ism</td>
                  <td style="padding:8px 0; font-weight:600;">{message['name']}</td></tr>
              <tr><td style="padding:8px 0; color:#6b7280;">📧 Email</td>
                  <td style="padding:8px 0;">
                    <a href="mailto:{message['email']}">{message['email']}</a>
                  </td></tr>
              <tr><td style="padding:8px 0; color:#6b7280;">🕒 Vaqt</td>
                  <td style="padding:8px 0;">{message['date']}</td></tr>
            </table>
            <hr style="border:none; border-top:1px solid #e5e7eb; margin:16px 0;">
            <p style="color:#374151; white-space:pre-wrap;">{message['message']}</p>
            <p style="color:#9ca3af; font-size:12px; margin-top:24px;">
              Bu xabar DevPortfolio saytidagi kontakt formasi orqali yuborilgan.
            </p>
          </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        # --- SSL orqali yuborish ---
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context, timeout=20) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, [EMAIL_RECEIVER], msg.as_string())

        print(f"✅ Email yuborildi → {EMAIL_RECEIVER}")
        return True

    except Exception as e:
        print(f"❌ Email yuborishda xatolik: {e}")
        return False


# ==================== API ENDPOINTS ====================
@app.route('/')
def serve_index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

@app.route('/api/health')
def health():
    return jsonify({
        "status": "online",
        "email_configured": bool(EMAIL_PASSWORD),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/projects', methods=['GET'])
def get_projects():
    return jsonify(PROJECTS)

@app.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = next((p for p in PROJECTS if p["id"] == project_id), None)
    if project:
        return jsonify(project)
    return jsonify({"error": "Project not found"}), 404

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify(STATS)

@app.route('/api/contact', methods=['POST'])
def contact():
    """Kontakt formadan kelgan xabarni qabul qiladi va emailga yuboradi"""
    data = request.get_json(silent=True)
    if not data or not data.get('name') or not data.get('email') or not data.get('message'):
        return jsonify({"success": False, "message": "Barcha maydonlarni to‘ldiring"}), 400

    # Oddiy email validatsiyasi
    email = data['email'].strip()
    if '@' not in email or '.' not in email.split('@')[-1]:
        return jsonify({"success": False, "message": "Email manzil noto‘g‘ri"}), 400

    message = {
        "id": len(MESSAGES) + 1,
        "name": data['name'].strip()[:100],
        "email": email[:120],
        "message": data['message'].strip()[:5000],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    MESSAGES.append(message)

    # Konsolga chiqarish (Render loglarida ko'rinadi)
    print(f"\n📨 New message from {message['name']} ({message['email']}):")
    print(f"   {message['message']}\n")

    # Emailga yuborish
    email_sent = send_email_notification(message)

    return jsonify({
        "success": True,
        "email_sent": email_sent,
        "message": "Xabar qabul qilindi! Tez orada javob beramiz."
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)