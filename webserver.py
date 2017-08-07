from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

# Database imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

# Accessing Database with ORM
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                restaurants = session.query(Restaurant).all()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                o_restaurants = ""
                for r in restaurants:
                    o_restaurants += (
                        r.name + "<br>"
                        + "<a href='/restaurants/%s/edit'>Edit</a><br>" % (r.id,)
                        + "<a href='/restaurants/%s/delete'>Delete</a><br>" % (r.id,)
                        + "<br>")
                output = (
                    "<html><body><a href=/restaurants/new>Add new "
                    "restaurant</a><br><br>" + o_restaurants
                    + "</body></html>")
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = (
                    '<html><body><h1>Make a New Restaurant</h1><br><form '
                    'action="/restaurants/add" method="post" '
                    'enctype="multipart/form-data"><label '
                    'for="r_name">Name:</label><input '
                    'id="r_name" type="text" name="name" '
                    'placeholder="My Restaurant"><input type="submit" '
                    'value="Save"></form></body></html>')
                self.wfile.write(output)
                print output
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            self.send_response(303)
            self.send_header('Content-type', 'text/html')
            self.send_header('Location', '/restaurants')
            self.end_headers()
            ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                r_name = fields.get('name')
                new_restaurant = Restaurant(name = r_name[0])
                session.add(new_restaurant)
                session.commit()
        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()