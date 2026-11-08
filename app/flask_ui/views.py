from flask import Blueprint, render_template, current_app

bp = Blueprint("ui", __name__)


@bp.route("/")
def index():
    return render_template("index.html", api_base="http://localhost:8000")
