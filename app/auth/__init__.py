from flask import Blueprint

# Membuat instance Blueprint.
# 'auth' adalah nama blueprint.
# __name__ membantu Flask menemukan lokasi blueprint.
bp = Blueprint('auth', __name__)

# Impor rute di bagian bawah untuk menghindari circular dependency
from app.auth import routes
