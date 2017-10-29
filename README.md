# Item Catalog App: Restaurant Menus

Result of an exercise in building an item catalog app, using a database and
basic CRUD operations, implementing authentication and authorization, and
providing API JSON endpoints.

## Obtain Google OAuth Credentials

1. Go to the Google API console
2. Click on *Credentials* / *Create credentials* / *OAuth client ID*
3. Choose *Web application*, fill out fields as following and click *Create* when
    done
  - *Name*: Whatever you want
  - *JS origins*: "http://localhost:5000"
  - *Redirect URIs*: "http://localhost:5000/login"
    and "http://localhost:5000/gconnect"
4. Go to *OAuth consent screen*
5. Fill out fields *Email address* and *Product name shown to users*
6. Save
7. Download JSON file from newly created OAuth client ID
8. Rename file to "client-secrets.json"

## How To Run

1. Clone repo to local folder
2. Put *client-secrets.json* with your credentials into same folder
3. Open console and cd into folder
4. Run `python database_setup.py` to setup database
5. Run `python lotsofmenus.py` to populate database (optional)
6. Run `python project.py` to start server
7. Open browser and visit http://localhost:5000/restaurants

## Notes

- *Add restaurant* and *Add menu item* buttons are only visible when logged in
- *Edit* and *Delete* buttons are only visible for items and restaurants that
  the logged-in user created
- All requests to create, update or delete are also blocked by the server, if
  the user does not have the necessary authorization

## JSON API

JSON endpoints can be reached by adding "/JSON" to the end of respective URI.
For example:

- http://localhost:5000/restaurants/JSON returns restaurant data for
  all restaurants
- http://localhost:5000/restaurants/1/JSON returns item data for all items of
  restaurant with restaurantID=1
- http://localhost:5000/restaurants/1/2/JSON returns item data for item with
  itemID=2 and restaurantID=1
