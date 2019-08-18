from flask import Blueprint
student = Blueprint("student", __name__, template_folder="templates", static_folder="static")
from app.student import routes
