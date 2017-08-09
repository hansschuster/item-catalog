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


# Show menu items for specific restaurant
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    output = ''
    for i in items:
        output += i.name + '<br>'
        output += i.price + '<br>'
        output += i.description + '<br><br>'
    return output


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
