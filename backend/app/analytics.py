#  Handles: /api/analytics/ summary and /api/analytics/history

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import models

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/analytics/summary', methods=['GET'])
@jwt_required()
def summary(): 
    user_id = int(get_jwt_identity())
    stats = models.get_analytics_summary(user_id)
    return jsonify({'summary': stats}), 200


@analytics_bp.route('/analytics/history', methods=['GET'])
@jwt_required()
def history(): 
    user_id = int(get_jwt_identity())
 
    try:
        days = int(request.args.get('days', 30))
        days = max(7, min(days, 365))    
    except ValueError:
        days = 30

    history_data = models.get_analytics_history(user_id, days)
    return jsonify({'history': history_data, 'days': days}), 200