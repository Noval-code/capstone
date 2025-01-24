from flask import request, jsonify, current_app,render_template
from database import db
from models.user_model import User
from flask_jwt_extended import create_access_token,jwt_required, get_jwt, get_jwt_identity
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import random
import logging

class AuthController:
    @staticmethod

    def home():
        render_template('index.html')
    def register():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"status":"error","message":"Invalid JSON"}), 400
            
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')

            if not username or not email or not password:
                return jsonify({
                    "status":"error",
                    "message":"All fields are required"
                }), 422
            
            if User.query.filter_by(username=username).first():
                return jsonify({
                    "status":"error",
                    "message":"username already been taken"
                }), 422
            
            if User.query.filter_by(email=email).first():
                return jsonify({
                    "status":"error",
                    "message":"email already been taken"
                }), 422
            
            otp = str(random.randint(100000,999999))

            new_user = User(
                username=username,
                email=email,
                is_verified=False,
                register_otp=otp,
                register_otp_created_at=datetime.utcnow(),
                reset_otp= '',
                reset_otp_created_at = None
            )
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            mail = Mail(current_app)
            msg = Message("YOUR OTP CODE",
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[email])
            msg.body = f"YOUR OTP code is :{otp}"

            try:
                mail.send(msg)
            except Exception as e:
                logging.error(f"Failed to send OTP email : {e}")
                db.session.delete(new_user)
                db.session.commit()
                return jsonify({
                    "status":"error",
                    "message":"Failed to send OTP email",
                    "error":str(e)
                }), 500
            
            return jsonify({
                "status":"success",
                "message":"Registration succesful. Please check your email for the OTP."
            }), 201
        
        except IntegrityError as e:
            db.session.rollback()
            logging.error(f"Database integrity error: {e}")
            return jsonify({
                "status":"error",
                "message":"Failed to register user due to database error",
                "error":str(e)
            }), 500
        
        except Exception as e:
            logging.error(f"Unexpected error during registration: {e}")
            return jsonify({
                "status":"error",
                "message":"An unexpected error occurred",
                "error":str(e)
            }), 500

    def verify_register_otp():
        data = request.get_json()
        email = data.get('email')
        otp = data.get('otp')

        if not email or not otp:
            return jsonify({
                "status": "error",
                "message": "Email and OTP are required"
            }), 422

        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 404

        if user.is_verified:
            return jsonify({
                "status": "success",
                "message": "User already verified",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            }), 200

        # Check if OTP matches
        if user.register_otp != otp:
            return jsonify({
                "status": "error",
                "message": "Invalid OTP"
            }), 401

        # Check if OTP is expired
        otp_expiry = user.register_otp_created_at + timedelta(minutes=current_app.config['OTP_EXPIRY_MINUTES'])
        if datetime.utcnow() > otp_expiry:
            return jsonify({
                "status": "error",
                "message": "OTP has expired. Please request a new one."
            }), 401

        # Verify user and clear OTP
        user.is_verified = True
        user.register_otp = None
        user.register_otp_created_at = None
        db.session.commit()

        # Generate JWT token
        access_token = create_access_token(identity={"id":user.id,"username": user.username})
        return jsonify({
            "status": "success",
            "message": "OTP verified successfully",
            "token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }), 200

    def resend_register_otp():
        try:
            data = request.get_json()
            email = data.get('email')

            if not email:
                return jsonify({
                    "status": "error",
                    "message": "Email is required"
                }), 422

            user = User.query.filter_by(email=email).first()

            if not user:
                return jsonify({
                    "status": "error",
                    "message": "User not found"
                }), 404

            if user.is_verified:
                return jsonify({
                    "status": "success",
                    "message": "User already verified"
                }), 200

            # Generate new OTP
            otp = str(random.randint(100000, 999999))
            user.register_otp = otp
            user.register_otp_created_at = datetime.utcnow()
            db.session.commit()

            # Send OTP via email
            mail = Mail(current_app)
            msg = Message("Your OTP Code",
                        sender=current_app.config['MAIL_USERNAME'],
                        recipients=[email])
            msg.body = f"Your OTP code is: {otp}"

            try:
                mail.send(msg)
            except Exception as e:
                logging.error(f"Failed to send OTP email: {e}")
                return jsonify({
                    "status": "error",
                    "message": "Failed to send OTP email",
                    "error": str(e)
                }), 500

            return jsonify({
                "status": "success",
                "message": "OTP sent successfully. Please check your email."
            }), 200

        except Exception as e:
            logging.error(f"Unexpected error in resend_otp: {e}")
            return jsonify({
                "status": "error",
                "message": "An unexpected error occurred",
                "error": str(e)
            }), 500

    def login():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({
                "status": "error",
                "message": "Email and password are required"
            }), 422

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return jsonify({
                "status": "error",
                "message": "Invalid credentials"
            }), 401

        if not user.is_verified:
            return jsonify({
                "status": "error",
                "message": "Please verify your email before logging in"
            }), 403

        # Generate access token
        access_token = create_access_token(identity={"id":user.id,"username": user.username})

        # Include user data in the response
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }), 200

    @jwt_required()
    def logout():
        jwt_payload = get_jwt()
        jti = jwt_payload["jti"]  # Token identifier
        revoked_tokens.add(jti)  # Tambahkan token ke revoked_tokens
        return jsonify({
            "status": "success",
            "message": "Logged out successfully"
        }), 200

    @jwt_required()
    def update_profile():
        user_identity = get_jwt_identity()  # Ambil data dari token
        current_user = User.query.get(user_identity['id'])
        
        if not current_user:
            return jsonify({"status": "error", "message": "User not found"}), 404

        data = request.get_json()
        new_username = data.get('username')
        new_email = data.get('email')

        # Jika kedua field kosong, kirim pesan error
        if not new_username and not new_email:
            return jsonify({
                "status": "error",
                "message": "At least one field (username or email) must be provided"
            }), 400

        # Validasi jika username sudah digunakan oleh pengguna lain
        if new_username and User.query.filter(User.username == new_username, User.id != current_user.id).first():
            return jsonify({
                "status": "error",
                "message": "Username is already taken"
            }), 422

        # Validasi jika email sudah digunakan oleh pengguna lain
        if new_email and User.query.filter(User.email == new_email, User.id != current_user.id).first():
            return jsonify({
                "status": "error",
                "message": "Email is already taken"
            }), 422

        # Update hanya field yang diberikan
        if new_username:
            current_user.username = new_username
        if new_email:
            current_user.email = new_email

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Profile updated successfully",
            "data": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email
            }
        }), 200

    def forgot_password():
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({"status": "error", "message": "Email is required"}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"status": "error", "message": "Email not found"}), 404

        # Generate OTP dan simpan ke database
        reset_otp = str(random.randint(100000, 999999))
        user.reset_otp = reset_otp
        user.reset_otp_created_at = datetime.utcnow()
        db.session.commit()

        # Kirim email OTP
        mail = Mail(current_app)
        msg = Message("Password Reset OTP",
                    sender=current_app.config['MAIL_USERNAME'],
                    recipients=[email])
        msg.body = f"Your OTP code to reset your password is: {reset_otp}"
        try:
            mail.send(msg)
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": "Failed to send OTP email",
                "error": str(e)
            }), 500

        # Kembalikan data user
        user_data = {
            "id": user.id,
            "usernamename": user.username,
            "email": user.email
        }
        return jsonify({"status": "success", "message": "OTP sent to email", "user": user_data}), 200

    def verify_reset_otp():
        data = request.get_json()
        email = data.get('email')
        otp = data.get('otp')

        if not email or not otp:
            return jsonify({"status": "error", "message": "Email and OTP are required"}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404

        # Periksa OTP dan masa berlakunya
        otp_expiry = user.reset_otp_created_at + timedelta(minutes=current_app.config['OTP_EXPIRY_MINUTES'])
        if user.reset_otp != otp or datetime.utcnow() > otp_expiry:
            return jsonify({"status": "error", "message": "Invalid or expired OTP"}), 400

        return jsonify({"status": "success", "message": "OTP verified"}), 200
        
    def resend_reset_otp():
        try:
            data = request.get_json()
            email = data.get('email')

            if not email:
                return jsonify({
                    "status": "error",
                    "message": "Email is required"
                }), 422

            user = User.query.filter_by(email=email).first()

            if not user:
                return jsonify({
                    "status": "error",
                    "message": "User not found"
                }), 404

            if user.is_verified:
                return jsonify({
                    "status": "success",
                    "message": "User already verified"
                }), 200

            # Generate new OTP
            otp = str(random.randint(100000, 999999))
            user.reset_otp = otp
            user.reset_otp_created_at = datetime.utcnow()
            db.session.commit()

            # Send OTP via email
            mail = Mail(current_app)
            msg = Message("Your OTP Code",
                        sender=current_app.config['MAIL_USERNAME'],
                        recipients=[email])
            msg.body = f"Your OTP code is: {otp}"

            try:
                mail.send(msg)
            except Exception as e:
                logging.error(f"Failed to send OTP email: {e}")
                return jsonify({
                    "status": "error",
                    "message": "Failed to send OTP email",
                    "error": str(e)
                }), 500

            return jsonify({
                "status": "success",
                "message": "OTP sent successfully. Please check your email."
            }), 200

        except Exception as e:
            logging.error(f"Unexpected error in resend_otp: {e}")
            return jsonify({
                "status": "error",
                "message": "An unexpected error occurred",
                "error": str(e)
            }), 500

    def reset_password():
        data = request.get_json()
        email = data.get('email')
        new_password = data.get('new_password')

        if not email or not new_password:
            return jsonify({"status": "error", "message": "Email and new password are required"}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404

        # Reset password
        user.set_password(new_password)
        user.reset_otp = None
        user.reset_otp_created_at = None
        db.session.commit()

        return jsonify({"status": "success", "message": "Password updated successfully"}), 200

    @jwt_required()
    def reset_password_loggedin():
        user_identity = get_jwt_identity()
        current_user = User.query.get(user_identity['id'])

        data = request.get_json()
        new_password = data.get('new_password')

        if not new_password:
            return jsonify({"status": "error", "message": "New password is required"}), 400

        # Update password
        current_user.set_password(new_password)
        db.session.commit()

        return jsonify({"status": "success", "message": "Password updated successfully"}), 200

    @jwt_required()
    def delete_user():
        user_identity = get_jwt_identity()
        current_user = User.query.get(user_identity['id'])

        if not current_user:
            return jsonify({"status": "error", "message": "User not found"}), 404

        # Hapus user dari database
        db.session.delete(current_user)
        db.session.commit()

        return jsonify({"status": "success", "message": "User deleted successfully"}), 200

    def get_all_users():
        try:
            # Ambil semua user dari database
            users = User.query.all()
            user_list = [{
                "id": user.id,
                "username": user.username,
                "email": user.email
            } for user in users]

            return jsonify({
                "status": "success",
                "data": user_list
            }), 200
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500

    def list_users():
        # Ambil token user dan verifikasi
        users = User.query.all()
        return render_template('list_users.html', users=users)
