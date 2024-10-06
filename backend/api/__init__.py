from flask import Blueprint

bp = Blueprint('api', __name__)

from . import auth, bot, projects, user