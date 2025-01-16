from flask import Blueprint

home = Blueprint('home', __name__, static_folder="static", template_folder="templates")

from website.blueprints.home import routes