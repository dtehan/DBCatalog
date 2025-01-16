from flask import Blueprint

search = Blueprint('search', __name__, static_folder="static", template_folder="templates")

from website.blueprints.search import routes