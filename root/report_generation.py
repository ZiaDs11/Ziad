from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_mail import Mail, Message
from models import User, Task
from datetime import datetime, timedelta

mail = Mail()

def configure_mail(app):
    mail.init_app(app)

report_bp = Blueprint('report_bp', __name__)

@report_bp.route('/generate_report', methods=['POST'])
@jwt_required()
def generate_report():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    frequency = request.json.get('frequency')

    # Time delta based on frequency
    time_delta = {
        'daily': timedelta(days=1),
        'weekly': timedelta(weeks=1),
        'monthly': timedelta(days=30)
    }.get(frequency, timedelta(days=1))

    end_time = datetime.now()
    start_time = end_time - time_delta

    tasks = Task.query.filter(
        Task.user_id == user_id,
        Task.due_date.between(start_time, end_time)
    ).all()

    task_details = ''.join([f"<li>{task.title} - {task.status}</li>" for task in tasks])

    email_body = f"""
    <h2>Task Report ({frequency.capitalize()})</h2>
    <ul>{task_details}</ul>
    """
    msg = Message(
        subject="Your Task Report",
        sender="Hello@Vodafone.com",
        recipients=[user.email],
        html=email_body
    )
    mail.send(msg)
    return jsonify({"message": "Report generated and sent"}), 200
