from config import Config
from flask import Flask, render_template, redirect, url_for
from database import db
from routes.auth_routes import auth_user_bp
from flask_mail import Mail
from flask_jwt_extended import JWTManager, jwt_required, get_jwt

app = Flask(__name__,template_folder='templates')
app.config.from_object(Config)

# inisialisasi JWT
jwt = JWTManager(app)
db.init_app(app)
revoked_tokens = set()
mail = Mail(app)

# callback untuk mengecek token di blacklist 
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header,jwt_payload):
    jti = jwt_payload["jti"]
    print(f"Revoked token : {jti}")
# registrasi blueprint
app.register_blueprint(auth_user_bp)

@app.route('/',methods=['GET'])
def home():
    """Root langsung mengarahkan ke login."""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)