# all the imports
import os
import sqlite3
from .samples import Samples
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask(__name__)
app.config.from_object(__name__) # load config from this file , auron.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'auron.db'),
    SECRET_KEY=os.urandom(42),
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('AURON_SETTINGS', silent=True)

#Database functions
def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.cli.command('populatedb')
def populatedb_command():
	"""Populates the database with sample values"""
	db = get_db()
	db.executemany('insert into products (name, price, description) values (?,?,?)', 
		Samples.samples)
	db.commit()

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

#Core functionality
@app.route('/')
def show_products():
    db = get_db()
    cur = db.execute('select name, price, description from products order by id desc')
    products = cur.fetchall()
    return render_template('show_products.html', products=products)

@app.route('/add', methods=['POST'])
def add_to_cart():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into cart (name, price) values (?, ?)',
                 [request.form['name'], request.form['price']])
    db.commit()
    return redirect(url_for('show_cart'))

@app.route('/cart')
def show_cart():
	if not session.get('logged_in'):
		abort(401)
	db = get_db()
	cur = db.execute('select id, name, price from cart')
	cart = cur.fetchall()
	total = sum([product['price'] for product in cart])
	return render_template('show_cart.html', cart=cart, total=total)

@app.route('/delete', methods=['POST'])
def delete_from_cart():
	if not session.get('logged_in'):
		abort(401)
	db = get_db()
	db.execute('delete from cart where id = ?', request.form['id'])
	db.commit()
	return redirect(url_for('show_cart'))

#Login system
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_products'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_products'))


