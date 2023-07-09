from flask import Blueprint, render_template, session, request, redirect, flash
from mysql import connector as sql
import random

store = Blueprint('store', __name__, url_prefix='/store', template_folder='templates_store',
                  static_folder='templates_store/assets')

db = sql.connect(
    host="localhost",
    user="root",
    passwd="qwertyuiop",
    database="Final_DBMS"
)


def execute(query):
    try:
        cursor = db.cursor()
        cursor.execute(query)
        res = cursor.fetchall()
        db.commit()
        return res

    except sql.Error as err:
        print(err)
        return -1


def fetchCart(loginid):
    _cart = "SELECT * FROM CartView WHERE ordid = '{}'".format(loginid)
    cart = execute(_cart)
    cart_total = 0
    for item in cart:
        cart_total += item[2]
    return cart, cart_total


@store.route('/')
def index():
    if 'user' in session and session['user']:
        loginid, usertype = session['user']

        _Products = "SELECT * FROM Products"
        Products = execute(_Products)

        _clothes = "SELECT * FROM Products WHERE catid = 1"
        clothes = execute(_clothes)

        _footwears = "SELECT * FROM Products WHERE catid = 2"
        footwears = execute(_footwears)

        _eappliances = "SELECT * FROM Products WHERE catid = 3"
        eappliances = execute(_eappliances)

        cart, cart_total = fetchCart(loginid)

        if Products == -1 or clothes == -1 or footwears == -1 or eappliances == -1 or cart == -1:
            return render_template('error-404.html')

        random.shuffle(Products)
        random.shuffle(clothes)
        random.shuffle(footwears)
        random.shuffle(eappliances)

        return render_template('index.html', Products=Products[:10], Clothes=clothes[:8],
                               Footwears=footwears[:8], Eappliances=eappliances[:8], Cart=cart, CartTotal=cart_total)
    else:
        return redirect('/auth')


@store.route('/account')
def account():
    if 'user' in session and session['user']:
        return redirect('/user')
    else:
        return redirect('/auth')


@store.route('/products')
def products():
    if 'user' in session and session['user']:
        loginid, usertype = session['user']

        _Products = "SELECT * FROM Products"
        Products = execute(_Products)

        cart, cart_total = fetchCart(loginid)

        if Products == -1 or cart == -1:
            return render_template('error-404.html')

        random.shuffle(Products)
        return render_template('products.html', Products=Products, Cart=cart, CartTotal=cart_total)
    else:
        return redirect('/auth')


@store.route('/product<int:id>')
def product(id):

    if 'user' in session and session['user']:
        loginid, usertype = session['user']

        _count = "SELECT COUNT(*) FROM Products"
        count = execute(_count)[0][0]

        if id < 1:
            id = count
        elif id > count:
            id = 1

        _product = "SELECT * FROM Products WHERE pdid = '{}'".format(id)
        product = execute(_product)

        if product == -1:
            return render_template('error-404.html')

        if product[0][1] == 1:
            _attr = "SELECT * FROM Clothes WHERE pdid = '{}'".format(id)
        elif product[0][1] == 2:
            _attr = "SELECT * FROM Footwears WHERE pdid = '{}'".format(id)
        elif product[0][1] == 3:
            _attr = "SELECT * FROM Eappliances WHERE pdid = '{}'".format(id)
        else:
            return render_template('error-404.html')

        attr = execute(_attr)
        cart, cart_total = fetchCart(loginid)

        if attr == -1 or cart == -1:
            return render_template('error-404.html')

        return render_template('productview.html', Product=product[0], Attr=attr, Cart=cart, CartTotal=cart_total)

    else:
        return redirect('/auth')


@store.route('/clothes')
def clothes():
    if 'user' in session and session['user']:
        loginid, usertype = session['user']
        cart, cart_total = fetchCart(loginid)

        _view = "INSERT INTO Views(uid, catid) VALUES('{}', 1)".format(loginid)
        execute(_view)

        _clothes = "SELECT * FROM Products WHERE catid = 1"
        clothes = execute(_clothes)

        return render_template('clothes.html', Clothes=clothes, Cart=cart, CartTotal=cart_total)
    else:
        return redirect('/auth')


@store.route('/footwears')
def footwears():
    if 'user' in session and session['user']:
        loginid, usertype = session['user']
        cart, cart_total = fetchCart(loginid)

        _footwears = "SELECT * FROM Products WHERE catid = 2"
        footwears = execute(_footwears)

        _view = "INSERT INTO Views(uid, catid) VALUES('{}', 2)".format(loginid)
        execute(_view)

        return render_template('footwears.html', Footwears=footwears, Cart=cart, CartTotal=cart_total)
    else:
        return redirect('/auth')


@store.route('/eappliances')
def eappliances():
    if 'user' in session and session['user']:
        loginid, usertype = session['user']
        cart, cart_total = fetchCart(loginid)

        _eappliances = "SELECT * FROM Products WHERE catid = 3"
        eappliances = execute(_eappliances)

        _view = "INSERT INTO Views(uid, catid) VALUES('{}', 3)".format(loginid)
        execute(_view)

        return render_template('eappliances.html', Eappliances=eappliances, Cart=cart, CartTotal=cart_total)
    else:
        return redirect('/auth')
