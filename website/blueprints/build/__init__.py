from flask import Blueprint

build = Blueprint('build', __name__, static_folder="static", template_folder="templates")

from website.blueprints.build import routes