from flask import (Flask, render_template, url_for, request, redirect, flash,
                   jsonify)

# Database imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, User

# Imports for login, authorization...
from flask import session as login_session, make_response, abort
import random
import string
import httplib2
import json
import requests
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from functools import wraps

# Accessing Database with ORM
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)
app.secret_key = 'super_secret_key'

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Test Menu App"


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        flash("You are not allowed to access there! Please log in first!")
        return redirect(url_for('login'))
    return decorated_function


# Show restaurants
@app.route('/restaurants/')
def restaurants():
    button_hide = 'hide'
    user_id = ''
    url_to = 'login'
    button_text = 'Login'
    if 'username' in login_session:
        button_hide = ''
        user_id = login_session['user_id']
        url_to = 'gdisconnect'
        button_text = 'Logout'
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants,
                           button_hide=button_hide, user_id=user_id,
                           url_to=url_to, button_text=button_text)


# Add new restaurant
@app.route('/restaurants/new/', methods=['GET', 'POST'])
@login_required
def newRestaurant():
    if request.method == 'POST':
        new_restaurant = Restaurant(name=request.form['name'],
                                    user_id=login_session['user_id'])
        session.add(new_restaurant)
        session.commit()
        flash('New restaurant created!')
        return redirect(url_for('restaurants'))
    else:
        return render_template('new_restaurant.html')


# Edit specified restaurant
@app.route('/restaurants/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
@login_required
def editRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if restaurant.user_id != login_session['user_id']:
        abort(403)
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
@login_required
def deleteRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if restaurant.user_id != login_session['user_id']:
        abort(403)
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
    button_hide = 'hide'
    user_id = ''
    url_to = 'login'
    button_text = 'Login'
    if 'username' in login_session:
        button_hide = ''
        user_id = login_session['user_id']
        url_to = 'gdisconnect'
        button_text = 'Logout'
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = (session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
             .all())
    return render_template('menu.html', restaurant=restaurant, items=items,
                           button_hide=button_hide, user_id=user_id,
                           url_to=url_to, button_text=button_text)


# Add menu item for specific restaurant
@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET', 'Post'])
@login_required
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        new_item = MenuItem(name=request.form['name'],
                            restaurant_id=restaurant_id,
                            price=request.form['price'],
                            course=request.form['course'],
                            description=request.form['description'],
                            user_id=login_session['user_id'])
        session.add(new_item)
        session.commit()
        flash('New menu item created')
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('new_menu_item.html',
                               restaurant_id=restaurant_id)


# Edit menu item
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/',
           methods=['GET', 'POST'])
@login_required
def editMenuItem(restaurant_id, menu_id):
    edit_item = session.query(MenuItem).filter_by(id=menu_id).one()
    if edit_item.user_id != login_session['user_id']:
        abort(403)
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
           methods=['GET', 'POST'])
@login_required
def deleteMenuItem(restaurant_id, menu_id):
    delete_item = session.query(MenuItem).filter_by(id=menu_id).one()
    if delete_item.user_id != login_session['user_id']:
        abort(403)
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


# Connect with Google OAuth2
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    print login_session['username'], data

    # Create User if not existent
    user_id = getUserID(login_session['email'])
    if not user_id:
        createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style = "width: 300px; height: 300px;border-radius: 150px;'
               '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> ')
    flash("you are now logged in as {}".format(login_session['username']))
    print "done!"
    return output


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Logout, revoke token
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = ('https://accounts.google.com/o/oauth2/revoke?token={}'
           .format(login_session['access_token']))
    h = httplib2.Http()
    result = h.request(url, 'GET')
    print 'result is '
    print result[0]['status']
    print json.loads(result[1]).get('error')
    if (result[0]['status'] == '200' or
            json.loads(result[1]).get('error') == 'invalid_token'):
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given '
                                            'user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
