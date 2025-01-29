from flask import Blueprint, render_template
from controllers.mobile_auth import MobileAuth

mobile_auth = Blueprint('mobie_auth', __name__, url_prefix='/mobile_auth')

# route list
# Register
mobile_auth.route('/api/register', methods=['POST'])(MobileAuth.register)
# verify register otp
mobile_auth.route('/api/verify_register_otp', methods=['POST'])(MobileAuth.verify_register_otp)
# resend register otp
mobile_auth.route('/api/resend_register_otp', methods=['POST'])(MobileAuth.resend_register_otp)
# login
mobile_auth.route('/api/login', methods=['POST'])(MobileAuth.login)
# logout
mobile_auth.route('/api/logout', methods=['POST'])(MobileAuth.logout)
# update profile
mobile_auth.route('/api/logout', methods=['PUT'])(MobileAuth.update_profile)
# forgot password
mobile_auth.route('/api/forgot-password', methods=['POST'])(MobileAuth.forgot_password)
# verify reset password otp
mobile_auth.route('/api/verify-reset-otp', methods=['POST'])(MobileAuth.verify_reset_otp)
# resend reset password otp
mobile_auth.route('/api/resend-reset-otp', methods=['POST'])(MobileAuth.resend_reset_otp)
# reset password
mobile_auth.route('/api/reset-password', methods=['POST'])(MobileAuth.reset_password)
# reset password loggedin
mobile_auth.route('/api/reset-password-loggedin', methods=['POST'])(MobileAuth.reset_password_loggedin)
# delete user
mobile_auth.route('/api/delete-user', methods=['DELETE'])(MobileAuth.delete_user)
mobile_auth.route('/api/users', methods=['DELETE'])(MobileAuth.get_all_users)
mobile_auth.route('/api/list-users', methods=['DELETE'])(MobileAuth.list_users)

mobile_auth.route('/home', methods=['GET'])(MobileAuth.home)