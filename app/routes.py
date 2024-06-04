from flask import Blueprint, request, jsonify, render_template, send_file, abort
from app.database import isValidToken, checkProfileToken, insert_new_profile, updateInfo, addingPhoto, Balance, delete_profile, getPhotos
from app.utils import getAnswer, resize_image_base64
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def log_request(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.is_json:
            json_data = request.get_json().copy()
            if 'photos' in json_data:
                del json_data['photos']
            logger.info(f"Request body: {json_data}")
        else:
            logger.info("Request body is not in JSON format")
        response = f(*args, **kwargs)
        logger.info(f"Response: {response.get_json() if response.is_json else 'Response is not in JSON format'}")
        return response
    return wrapper

bp = Blueprint('routes', __name__)

@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

def register_routes(app):
    app.register_blueprint(bp)
