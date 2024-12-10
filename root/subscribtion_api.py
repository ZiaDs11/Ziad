from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from datetime import datetime, timedelta

from models import User, Task, Subscription
from db import db
from flask_mail import Mail  

subscription_api = Blueprint('subscription_api', __name__)

@subscription_api.route('/subscribe', methods=['POST'])
@jwt_required()
def subscribe():
    """
    Allows the user to subscribe to periodic task report notifications.
    The user will receive tasks with an end date within the selected range (daily/weekly/monthly).
    """

    user_id = get_jwt_identity()
    data = request.get_json()

    try:
        # Parse and validate 'start_date'
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d %H:%M:%S')
        if start_date.minute != 0 or start_date.second != 0:
            return jsonify({"error": "start_date must have valid hours (00-23) and no minutes or seconds"}), 400

        # Parse and validate 'frequency'
        frequency = data.get('frequency')
        if frequency not in ['daily', 'weekly', 'monthly']:
            return jsonify({"error": "Invalid frequency. Choose from: daily, weekly, monthly"}), 400

        # Parse 'report_time'
        report_time = datetime.strptime(data['report_time'], '%H:%M:%S').time()

        # Create subscription in database
        subscription = Subscription(
            user_id=user_id,
            frequency=frequency,
            start_date=start_date,
            report_time=report_time
        )
        db.session.add(subscription)
        db.session.commit()

        return jsonify({"message": "Subscription created successfully"}), 201

    except ValueError:
        return jsonify({"error": "Invalid date or time format"}), 400


def fetch_tasks(user_id, frequency):
    """
    Fetch tasks based on the frequency and filter by their end_date range.
    """
    now = datetime.now()

    if frequency == "daily":
        # Fetch tasks with end_date between today and now
        start_period = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_period = now
    elif frequency == "weekly":
        # Fetch tasks from the last 7 days
        start_period = now - timedelta(days=7)
        end_period = now
    elif frequency == "monthly":
        # Fetch tasks from the last 30 days
        start_period = now - timedelta(days=30)
        end_period = now
    else:
        return []

    # Query database for tasks that belong to the user and match the end date range
    tasks = Task.query.filter(
        Task.user_id == user_id,
        Task.end_date >= start_period,
        Task.end_date <= end_period
    ).all()
    
    return tasks


def send_periodic_email(user_id, tasks):
    """
    Sends an email containing the fetched tasks to the user.
    """
    if not tasks:
        # If no tasks are found, return gracefully
        return

    # Format the content for email
    task_list = "\n".join([f"Task Name: {task.name}, End Date: {task.end_date}" for task in tasks])

    email_body = f"Hello, here are the tasks that matched your report criteria:\n\n{task_list}\n\nThank you!"
    
    # Send the email
    user_email = "user@example.com"  # Fetch the user email from database if necessary
    Mail(user_email, subject="Periodic Task Report", body=email_body)
    

# Background Scheduler or Cron Job (pseudo-code)
def scheduler():
    """
    Pseudo code: Replace this with actual background scheduler logic.
    This should run daily at the `report_time` specified in Subscription.
    """
    subscriptions = Subscription.query.all()
    for sub in subscriptions:
        # Check if the current time matches the subscription's report_time
        now = datetime.now()
        if now.hour == sub.report_time.hour:
            # Fetch user's tasks
            tasks = fetch_tasks(sub.user_id, sub.frequency)
            # Send email
            send_periodic_email(sub.user_id, tasks)
@subscription_api.route('/unsubscribe', methods=['DELETE'])
@jwt_required()
def unsubscribe():
    user_id = get_jwt_identity()

    # Fetch the subscription for the authenticated user
    subscription = Subscription.query.filter_by(user_id=user_id).first()

    if not subscription:
        return jsonify({"message": "No subscription found for the user"}), 404

    # Delete the subscription
    db.session.delete(subscription)
    db.session.commit()

    return jsonify({"message": "Subscription deleted successfully"}), 200
