from flask import Flask
from flask_cors import CORS
import logging
import os
from app.database import db_init
from app.routes import register_routes

def create_app():
    app = Flask(__name__)
    if not os.path.exists('instance'):
        os.makedirs(app.instance_path)

    # Инциализация CORS
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Инициализация базы данных
    db_init(app)

    # Включение логгирования
    if not os.path.exists('logs'):
        os.makedirs('logs')

    file_handler = logging.FileHandler("logs/app.log", encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    # Инициализация роутов
    register_routes(app)

    return app
