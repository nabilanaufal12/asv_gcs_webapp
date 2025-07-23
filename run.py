# DIUBAH: Tambahkan monkey_patch di baris paling atas
import eventlet
eventlet.monkey_patch()

from app import create_app, db, socketio
from app.models import User

# Buat instance aplikasi menggunakan factory
app = create_app()

@app.shell_context_processor
def make_shell_context():
    """
    Membuat konteks shell agar kita bisa bekerja dengan database
    dan model di terminal Flask.
    """
    return {'db': db, 'User': User}

if __name__ == '__main__':
    with app.app_context():
        # Buat semua tabel database jika belum ada
        db.create_all()

        # Buat pengguna default jika belum ada
        if not User.query.filter_by(username='admin').first():
            print("Membuat pengguna default: admin")
            default_user = User(username='admin')
            # Atur password default ke 'password'
            default_user.set_password('password')
            db.session.add(default_user)
            db.session.commit()
            print("Pengguna 'admin' dengan password 'password' telah dibuat.")

    # Jalankan aplikasi menggunakan server SocketIO
    print("Menjalankan server dengan SocketIO dan Eventlet...")
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
