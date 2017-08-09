from flask import Flask
app = Flask(__name__)

# Database imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

# Accessing Database with ORM
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
