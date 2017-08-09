from flask import Flask, render_template, url_for, request, redirect
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
    return render_template('menu.html', restaurant=restaurant, items=items)


# Add menu item for specific restaurant
@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET', 'Post'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        new_item = MenuItem(name=request.form['name'],
                           restaurant_id=restaurant_id)
        session.add(new_item)
        session.commit()
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('new_menu_item.html',
                               restaurant_id=restaurant_id)


# Edit menu item
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/',
          methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    edit_item = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            edit_item.name = request.form['name']
        session.add(edit_item)
        session.commit()
        return redirect(url_for('restaurantMenu',
                                restaurant_id = restaurant_id))
    else:
        return render_template('edit_menu_item.html',
                               restaurant_id=restaurant_id,
                               menu_id=menu_id,
                               edit_item=edit_item)


# Delete menu item
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/')
def deleteMenuItem(restaurant_id, menu_id):
    return "page to delete a menu item. Task 3 complete!"


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
