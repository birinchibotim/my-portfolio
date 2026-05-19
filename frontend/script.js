// API manzili (Render’da avtomatik to‘g‘rilanadi)
const API_BASE = window.location.origin;

// Stats yuklash
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const stats = await response.json();
        document.getElementById('stat-projects').textContent = stats.projects;
        document.getElementById('stat-exp').textContent = stats.experience_months;
        document.getElementById('stat-tech').textContent = stats.technologies;
    } catch (error) {
        console.error('Stats yuklanmadi:', error);
    }
}

// Loyihalarni yuklash
async function loadProjects() {
    try {
        const response = await fetch(`${API_BASE}/api/projects`);
        if (!response.ok) throw new Error('Network error');
        const projects = await response.json();
        
        const grid = document.getElementById('projects-grid');
        if (projects.length === 0) {
            grid.innerHTML = '<div class="loading">Hozircha loyihalar yo‘q</div>';
            return;
        }
        
        grid.innerHTML = projects.map(project => `
            <div class="project-card">
                <div class="project-icon">${project.icon}</div>
                <h3>${project.title}</h3>
                <p>${project.description}</p>
                <div class="tech-stack">
                    ${project.tech.map(t => `<span class="tech">${t}</span>`).join('')}
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Loyihalar yuklanmadi:', error);
        document.getElementById('projects-grid').innerHTML = '<div class="loading">⚠️ Loyihalarni yuklab bo‘lmadi. Iltimos, keyinroq urinib ko‘ring.</div>';
    }
}

// Kontakt formani yuborish
document.getElementById('contact-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submit-btn');
    const statusDiv = document.getElementById('form-status');
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const message = document.getElementById('message').value.trim();
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Yuborilmoqda...';
    statusDiv.innerHTML = '';
    
    try {
        const response = await fetch(`${API_BASE}/api/contact`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, message })
        });
        
        const data = await response.json();
        if (response.ok && data.success) {
            statusDiv.innerHTML = `<div class="success">✅ ${data.message}</div>`;
            document.getElementById('contact-form').reset();
        } else {
            throw new Error(data.message || 'Xatolik yuz berdi');
        }
    } catch (error) {
        statusDiv.innerHTML = `<div class="error">❌ Xabar yuborilmadi: ${error.message}</div>`;
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Yuborish';
    }
});

// Mobil menyu
const burger = document.querySelector('.burger');
const navLinks = document.querySelector('.nav-links');
if (burger) {
    burger.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        burger.classList.toggle('toggle');
    });
}

// Sahifa yuklanganda
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadProjects();
    
    // Backend holatini tekshirish (ixtiyoriy)
    fetch(`${API_BASE}/api/health`)
        .then(r => r.json())
        .then(data => console.log('✅ Backend online:', data))
        .catch(err => console.error('❌ Backend xatosi:', err));
});