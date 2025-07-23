from flask import render_template
from flask_login import login_required
from app.main import bp

@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    """Menampilkan halaman dasbor utama."""
    return render_template('main/dashboard.html', title='Dashboard')
