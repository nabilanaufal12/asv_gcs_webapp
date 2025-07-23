from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class User(UserMixin, db.Model):
    """Model database untuk pengguna (User)."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    waypoints = db.relationship('Waypoint', backref='author', lazy='dynamic', cascade="all, delete-orphan")

    # DIUBAH: Menambahkan kolom untuk menyimpan pengaturan
    pid_kp = db.Column(db.Float, default=1.0)
    pid_ki = db.Column(db.Float, default=0.1)
    pid_kd = db.Column(db.Float, default=0.5)
    servo_min = db.Column(db.Integer, default=45)
    servo_max = db.Column(db.Integer, default=135)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_pid_gains(self):
        """Mengembalikan pengaturan PID sebagai dictionary."""
        return {"kp": self.pid_kp, "ki": self.pid_ki, "kd": self.pid_kd}

    def get_servo_limits(self):
        """Mengembalikan batas servo sebagai dictionary."""
        return {"min": self.servo_min, "max": self.servo_max}

    def __repr__(self):
        return f'<User {self.username}>'

class Waypoint(db.Model):
    """Model database untuk waypoint."""
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {'lat': self.lat, 'lon': self.lon}

    def __repr__(self):
        return f'<Waypoint {self.id} ({self.lat}, {self.lon})>'

@login_manager.user_loader
def load_user(id):
    """Memuat pengguna dari database berdasarkan ID."""
    return User.query.get(int(id))
