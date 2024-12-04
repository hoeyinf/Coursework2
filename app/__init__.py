"""Run when package loads. Set up application."""
from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_restful import Resource, Api

# Create a Flask application
app = Flask(__name__)
app.config.from_object('config')
api = Api(app)

# Create Bcrypt object
bcrypt = Bcrypt(app)

# Create and set login_manager
login_manager = LoginManager()
login_manager.init_app(app)

# AJAX task resources
tasks = {}


class TaskResource(Resource):
    def get(self, task_id):
        return {task_id: tasks[task_id]}

    def put(self, task_id):
        tasks[task_id] = request.form['data']
        return {task_id: tasks[task_id]}


api.add_resource(TaskResource, '/<string:task_id>')

# Initialize/migrate database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import views, models
