from flask_sqlalchemy import SQLAlchemy

# Initialize the database
db = SQLAlchemy()

# Import models after db to avoid circular imports
from . import sql_models
