from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()


def init_db(app):

    # SQLite database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///chicago_crime.db"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Connect SQLAlchemy with Flask
    db.init_app(app)