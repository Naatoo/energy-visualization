from flask import Blueprint


analyse = Blueprint('analyse', __name__)


from app.analyse import views
