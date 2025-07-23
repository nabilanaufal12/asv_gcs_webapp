from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO

# Inisialisasi ekstensi di luar factory
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
socketio = SocketIO()

def create_app(config_class=Config):
    """
    Factory function untuk membuat instance aplikasi Flask.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inisialisasi ekstensi dengan aplikasi
    db.init_app(app)
    login_manager.init_app(app)
    # Inisialisasi SocketIO dengan app dan mode async 'eventlet'
    socketio.init_app(app, async_mode='eventlet')

    # Impor dan daftarkan blueprint untuk otentikasi
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Impor dan daftarkan blueprint untuk fitur utama
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # Impor event handler dari file terpisah setelah semua diinisialisasi
    # Ini untuk menghindari circular imports dan memastikan handlers terdaftar.
    from .main import events

    return app
