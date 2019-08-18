from flask import Blueprint
user = Blueprint("user", __name__, template_folder="templates", static_folder="static")
from app.user import routes
