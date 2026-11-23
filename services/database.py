import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    database_path = os.environ.get(
        "DATABASE_PATH",
        os.path.join(app.instance_path, "chicago_crime.db")
    )

    os.makedirs(os.path.dirname(database_path), exist_ok=True)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + database_path
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)