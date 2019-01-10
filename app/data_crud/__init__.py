from flask import Blueprint


data = Blueprint('data_crud', __name__)


from app.data_crud import views
