from flask import Flask
from db import db
from user_authentication import auth_bp
from task_management_api import task_bp
from subscribtion_api import subscription_api
from report_generation import report_bp, configure_mail
from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required
#from utils.email_service import send_email 
from datetime import timedelta
import secrets


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Vodafone.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'e9d528eefc0f12b4c6fecd6b1e5a3c6a0d8bbfedfc23ee96b534eb2bb5fd0f12'
#app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # Adjust as needed
#app.config['JWT_SECRET_KEY'] = secrets.token_hex(32)  # Generates a 32-byte random key

#app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=12)

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ziad57448@gmail.com'
app.config['MAIL_PASSWORD'] = 'qbwt mjpr bwdy vkqe'

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)
configure_mail(app)
deleted_tasks=[]
# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(task_bp, url_prefix='/api')
app.register_blueprint(subscription_api, url_prefix='/subscription')
app.register_blueprint(report_bp, url_prefix='/reports')

if __name__ == '__main__':
    with app.app_context():
     jwt_required() 
     db.create_all()  # Create database tables
        # Static Tests
        
    # Start the app
    app.run(debug=True)
