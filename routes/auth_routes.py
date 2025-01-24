from flask import Blueprint, render_template
from controllers.auth_controller import AuthController

auth_user_bp = Blueprint('auth_user', __name__, url_prefix='/auth')

# route list
# Register
auth_user_bp.route('/api/register', methods=['POST'])(AuthController.register)
# verify register otp
auth_user_bp.route('/api/verify_register_otp', methods=['POST'])(AuthController.verify_register_otp)
# resend register otp
auth_user_bp.route('/api/resend_register_otp', methods=['POST'])(AuthController.resend_register_otp)
# login
auth_user_bp.route('/api/login', methods=['POST'])(AuthController.login)
# logout
auth_user_bp.route('/api/logout', methods=['POST'])(AuthController.logout)
# update profile
auth_user_bp.route('/api/logout', methods=['PUT'])(AuthController.update_profile)
# forgot password
auth_user_bp.route('/api/forgot-password', methods=['POST'])(AuthController.forgot_password)
# verify reset password otp
auth_user_bp.route('/api/verify-reset-otp', methods=['POST'])(AuthController.verify_reset_otp)
# resend reset password otp
auth_user_bp.route('/api/resend-reset-otp', methods=['POST'])(AuthController.resend_reset_otp)
# reset password
auth_user_bp.route('/api/reset-password', methods=['POST'])(AuthController.reset_password)
# reset password loggedin
auth_user_bp.route('/api/reset-password-loggedin', methods=['POST'])(AuthController.reset_password_loggedin)
# delete user
auth_user_bp.route('/api/delete-user', methods=['DELETE'])(AuthController.delete_user)
auth_user_bp.route('/api/users', methods=['DELETE'])(AuthController.get_all_users)
auth_user_bp.route('/api/list-users', methods=['DELETE'])(AuthController.list_users)

auth_user_bp.route('/home', methods=['GET'])(AuthController.home)