from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from db import db
from models import Task

# Task Blueprint
task_bp = Blueprint('tasks', __name__)

# A list to keep deleted tasks for restoration
deleted_tasks = []

@task_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    data = request.json

    if not data.get('title') or not data.get('due_date'):
        return jsonify({"message": "Title and Due Date are required"}), 400

    try:
        due_date = datetime.fromisoformat(data['due_date'])
    except ValueError:
        return jsonify({"message": "Invalid due date format"}), 400

    task = Task(
        title=data['title'],
        description=data.get('description'),
        start_date=datetime.utcnow(),
        due_date=due_date,
        status=data.get('status', 'Pending'),
        user_id=user_id
    )
    db.session.add(task)
    db.session.commit()

    return jsonify({"message": "Task created successfully", "task_id": task.id}), 201

@task_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Task.query.filter_by(user_id=user_id)

    if status:
        query = query.filter_by(status=status)

    if start_date and end_date:
        try:
            query = query.filter(Task.due_date.between(
                datetime.fromisoformat(start_date), datetime.fromisoformat(end_date)))
        except ValueError:
            return jsonify({"message": "Invalid date range"}), 400

    tasks = query.all()
    return jsonify([{ "id": task.id, "title": task.title, "description": task.description,
                      "start_date": task.start_date, "due_date": task.due_date,
                      "completion_date": task.completion_date, "status": task.status } for task in tasks])

@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({"message": "Task not found"}), 404

    data = request.json
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.status = data.get('status', task.status)

    if 'due_date' in data:
        try:
            task.due_date = datetime.fromisoformat(data['due_date'])
        except ValueError:
            return jsonify({"message": "Invalid due date format"}), 400

    db.session.commit()
    return jsonify({"message": "Task updated successfully"})

@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({"message": "Task not found"}), 404

    deleted_tasks.append(task)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted successfully"})

@task_bp.route('/tasks/restore', methods=['POST'])
@jwt_required()
def restore_task():
    user_id = get_jwt_identity()
    print(f"Authenticated user_id: {user_id}")
    if not deleted_tasks:
        return jsonify({"message": "No tasks to restore"}), 404

    task_to_restore = deleted_tasks.pop()
    print(f"Task user_id: {task_to_restore.user_id}")

    if task_to_restore.user_id != user_id:
        return jsonify({"message": "Unauthorized to restore this task"}), 403

    db.session.add(task_to_restore)
    db.session.commit()
    return jsonify({"message": "Task restored successfully"})
