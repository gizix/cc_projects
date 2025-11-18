"""API routes."""
from quart import Blueprint, jsonify

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.get('/hello')
async def hello():
    """Hello endpoint."""
    return jsonify(message="Hello from Quart!")
