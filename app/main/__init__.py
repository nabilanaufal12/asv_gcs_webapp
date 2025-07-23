from flask import Blueprint

# Membuat instance Blueprint untuk fitur utama aplikasi
bp = Blueprint('main', __name__)

# Impor rute di bagian bawah untuk menghindari circular dependency
from app.main import routes
