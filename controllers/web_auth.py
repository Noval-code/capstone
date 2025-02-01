from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models.user_model import User
from database import db
import random
from datetime import datetime, timedelta

web_auth = Blueprint("web_auth", __name__,url_prefix='/web_auth')

# 🔹 LOGIN PAGE
@web_auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("username dan password wajib diisi!", "danger")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if not user.is_verified:
                flash("Akun belum diverifikasi. Silakan cek email Anda.", "danger")
                return redirect(url_for("web_auth.verify"))

            login_user(user)
            session["user_id"] = user.id  # Simpan session
            flash("Login berhasil!", "success")
            return redirect(url_for("dashboard"))

        flash("Username atau password salah!", "danger")

    return render_template("auth/login.html")

# 🔹 LOGOUT
@web_auth.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop("user_id", None)
    flash("Logout berhasil!", "success")
    return redirect(url_for("web_auth.login"))

# 🔹 REGISTER
@web_auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(username=username).first():
            flash("Username sudah digunakan!", "danger")
            return redirect(url_for("web_auth.register"))

        if User.query.filter_by(email=email).first():
            flash("Email sudah digunakan!", "danger")
            return redirect(url_for("web_auth.register"))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        new_user.register_otp = str(random.randint(100000, 999999))
        new_user.register_otp_created_at = datetime.utcnow()
        db.session.add(new_user)
        db.session.commit()

        flash("Akun berhasil dibuat! Silakan verifikasi email Anda.", "info")
        return redirect(url_for("web_auth.verify"))

    return render_template("auth/register.html")

# 🔹 VERIFIKASI OTP
@web_auth.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        email = request.form.get("email")
        otp = request.form.get("otp")

        user = User.query.filter_by(email=email).first()
        if user and user.register_otp == otp:
            if user.register_otp_created_at and datetime.utcnow() - user.register_otp_created_at < timedelta(minutes=5):
                user.is_verified = True
                user.register_otp = None
                user.register_otp_created_at = None
                db.session.commit()
                flash("Verifikasi berhasil! Silakan login.", "success")
                return redirect(url_for("web_auth.login"))
            else:
                flash("OTP sudah kadaluarsa!", "danger")
        else:
            flash("OTP salah!", "danger")

    return render_template("auth/verify.html")
