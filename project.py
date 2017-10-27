from flask import (Flask, render_template, url_for, request, redirect, flash,
                   jsonify)

# Database imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

# Imports for login
from flask import session as login_session
import random, string

# Accessing Database with ORM
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

app = Flask(__name__)
app.secret_key = 'super_secret_key'


# Show restaurants
@app.route('/restaurants/')
def restaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants)


# Add new restaurant
@app.route('/restaurants/new/', methods=['GET', 'POST'])
def newRestaurant():
    if request.method == 'POST':
        new_restaurant = Restaurant(name=request.form['name'])
        session.add(new_restaurant)
        session.commit()
        flash('New restaurant created!')
        return redirect(url_for('restaurants'))
    else:
        return render_template('new_restaurant.html')


# Edit specified restaurant
@app.route('/restaurants/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        old_name = restaurant.name
        if request.form['name']:
            restaurant.name = request.form['name']
        session.add(restaurant)
        session.commit()
        flash('Renamed restaurant {} to {}'.format(old_name,
                                                   restaurant.name))
        return redirect(url_for('restaurants'))
    else:
        return render_template('edit_restaurant.html', restaurant=restaurant)


# Delete specified restaurant
@app.route('/restaurants/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurant)
        session.commit()
        flash('Deleted restaurant {}'.format(restaurant.name))
        return redirect(url_for('restaurants'))
    else:
        return render_template('delete_restaurant.html', restaurant=restaurant)


# Show menu items for specific restaurant
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = (session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
             .all())
    return render_template('menu.html', restaurant=restaurant, items=items)


# Add menu item for specific restaurant
@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET', 'Post'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        new_item = MenuItem(name=request.form['name'],
                            restaurant_id=restaurant_id,
                            price=request.form['price'],
                            course=request.form['course'],
                            description=request.form['description'])
        session.add(new_item)
        session.commit()
        flash('New menu item created')
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
        old_name = edit_item.name
        if request.form['name']:
            edit_item.name = request.form['name']
        if request.form['price']:
            edit_item.price = request.form['price']
        if request.form['course']:
            edit_item.course = request.form['course']
        if request.form['description']:
            edit_item.description = request.form['description']
        session.add(edit_item)
        session.commit()
        flash('Edited item {} (Former name: {})'.format(old_name,
                                                        edit_item.name))
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('edit_menu_item.html',
                               restaurant_id=restaurant_id,
                               menu_id=menu_id,
                               edit_item=edit_item)


# Delete menu item
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/',
           methods = ['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    delete_item = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        session.delete(delete_item)
        session.commit()
        flash('Deleted item {}'.format(delete_item.name))
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('delete_menu_item.html',
                               restaurant_id=restaurant_id,
                               menu_id=menu_id,
                               delete_item=delete_item)


# Send JSON data for restaurants
@app.route('/restaurants/JSON/')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurants=[r.serialize for r in restaurants])


# Send JSON data for menu items of specific restaurant
@app.route('/restaurants/<int:restaurant_id>/JSON/')
def restaurantMenuJSON(restaurant_id):
    items = (session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
             .all())
    return jsonify(MenuItems=[i.serialize for i in items])


# Send JSON data for specific menu item of specific restaurant
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/JSON/')
def menuItemJSON(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(restaurant_id=restaurant_id,
                                             id=menu_id).one()
    return jsonify(MenuItem=item.serialize)


# Create pseudo-random state token to make sure the user is making the request
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_lowercase +
                                  string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
