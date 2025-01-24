from database import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    register_otp = db.Column(db.String(6), nullable=True)
    register_otp_created_at = db.Column(db.DateTime, nullable=True)
    reset_otp = db.Column(db.String(6), nullable=True, default='')
    reset_otp_created_at = db.Column(db.DateTime, nullable=True, default=None)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password,method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
