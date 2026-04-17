# Handles api tasks and api categories 

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import models

tasks_bp = Blueprint('tasks', __name__)
 

@tasks_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks(): 
    user_id = int(get_jwt_identity())
 
    filters = {}

    if request.args.get('date'):
        filters['date'] = request.args.get('date')

    if request.args.get('week_start'):
        filters['week_start'] = request.args.get('week_start')

    if request.args.get('category'):
        filters['category'] = int(request.args.get('category'))

    if request.args.get('priority'):
        filters['priority'] = request.args.get('priority')

    # Parse 'true'/'false' string → Python bool
    if request.args.get('complete') is not None:
        complete_str = request.args.get('complete').lower()
        if complete_str in ('true', '1'):
            filters['complete'] = True
        elif complete_str in ('false', '0'):
            filters['complete'] = False

    tasks = models.get_tasks(user_id, filters)
    return jsonify({'tasks': tasks, 'count': len(tasks)}), 200


@tasks_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task(): 
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body must be JSON.'}), 400
 
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Task title is required.'}), 400

    if len(title) > 200:
        return jsonify({'error': 'Title must be 200 characters or fewer.'}), 400
 
    priority = data.get('priority', 'medium')
    if priority not in ('low', 'medium', 'high'):
        return jsonify({'error': "Priority must be 'low', 'medium', or 'high'."}), 400

    task = models.create_task(user_id, data)
    return jsonify({'message': 'Task created.', 'task': task}), 201


@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id): 
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body must be JSON.'}), 400
 
    existing = models.get_task_by_id(task_id, user_id)
    if not existing:
        return jsonify({'error': 'Task not found.'}), 404
 
    if 'title' in data:
        if not data['title'].strip():
            return jsonify({'error': 'Task title cannot be empty.'}), 400
        if len(data['title']) > 200:
            return jsonify({'error': 'Title must be 200 characters or fewer.'}), 400
 
    if 'priority' in data and data['priority'] not in ('low', 'medium', 'high'):
        return jsonify({'error': "Priority must be 'low', 'medium', or 'high'."}), 400

    task = models.update_task(task_id, user_id, data)
    return jsonify({'message': 'Task updated.', 'task': task}), 200


@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id): 
    user_id = int(get_jwt_identity())

    deleted = models.delete_task(task_id, user_id)
    if not deleted:
        return jsonify({'error': 'Task not found.'}), 404

    return jsonify({'message': 'Task deleted.'}), 200


@tasks_bp.route('/tasks/<int:task_id>/toggle', methods=['PATCH'])
@jwt_required()
def toggle_task(task_id): 
    user_id = int(get_jwt_identity())

    task = models.toggle_task(task_id, user_id)
    if not task:
        return jsonify({'error': 'Task not found.'}), 404

    status = 'completed' if task['is_complete'] else 'marked incomplete'
    return jsonify({'message': f'Task {status}.', 'task': task}), 200

 

@tasks_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories(): 
    user_id = int(get_jwt_identity())
    categories = models.get_categories(user_id)
    return jsonify({'categories': categories}), 200


@tasks_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category(): 
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body must be JSON.'}), 400

    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Category name is required.'}), 400

    if len(name) > 50:
        return jsonify({'error': 'Category name must be 50 characters or fewer.'}), 400

    color = data.get('color', '#6366f1')

    category = models.create_category(user_id, name, color)
    return jsonify({'message': 'Category created.', 'category': category}), 201


@tasks_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id): 
    user_id = int(get_jwt_identity())

    deleted = models.delete_category(category_id, user_id)
    if not deleted:
        return jsonify({'error': 'Category not found.'}), 404

    return jsonify({'message': 'Category deleted.'}), 200