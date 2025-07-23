import os
from dotenv import load_dotenv

# Muat variabel dari file .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """
    Konfigurasi dasar untuk aplikasi Flask.
    """
    # Kunci rahasia untuk melindungi sesi dan form dari serangan CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kunci-rahasia-yang-sangat-sulit-ditebak'

    # Konfigurasi database SQLAlchemy
    # Menggunakan SQLite untuk kemudahan setup awal
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
