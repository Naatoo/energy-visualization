import os

from app import create_app, setup_database

app = create_app()


if __name__ == '__main__':
    if not os.path.isfile('main_data.db'):
        setup_database(app)
    app.run(debug=True)

