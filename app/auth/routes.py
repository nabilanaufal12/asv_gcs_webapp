from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.auth import bp
from app.models import User, db

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Menangani logika untuk login pengguna.
    """
    # Jika pengguna sudah login, arahkan ke dasbor
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard')) # Kita akan buat rute ini nanti

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        # Periksa apakah pengguna ada dan passwordnya cocok
        if user is None or not user.check_password(password):
            flash('Username atau password salah', 'danger')
            return redirect(url_for('auth.login'))

        # Jika valid, loginkan pengguna
        login_user(user, remember=True)
        flash('Login berhasil!', 'success')
        
        # Arahkan ke halaman dasbor setelah login
        return redirect(url_for('main.dashboard')) # Akan dibuat nanti

    return render_template('auth/login.html', title='Login')

@bp.route('/logout')
@login_required
def logout():
    """
    Menangani logika untuk logout pengguna.
    """
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('auth.login'))
