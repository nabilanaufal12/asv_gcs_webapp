from flask import render_template
from flask_login import login_required
from app.main import bp

@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    """Menampilkan halaman dasbor utama (GCS Kontrol)."""
    return render_template('main/dashboard.html', title='Dashboard')

# DIUBAH: Menambahkan rute baru untuk halaman monitoring
@bp.route('/monitor')
def monitor():
    """Menampilkan halaman monitoring sederhana (read-only)."""
    # Halaman ini tidak memerlukan login
    return render_template('main/monitor.html', title='Live Monitor')
