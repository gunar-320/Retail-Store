import random

from flask import Blueprint, render_template, session, request, redirect, flash
import mysql.connector as sql
from datetime import date, timedelta

user = Blueprint('user', __name__, url_prefix='/user', template_folder='templates_store',
                 static_folder='templates_store/assets')

db = sql.connect(
    host="localhost",
    user="root",
    passwd="qwertyuiop",
    database="Final_DBMS"
)


def execute(query):
    global cursor
    try:
        cursor = db.cursor()
        cursor.execute(query)
        res = cursor.fetchall()
        db.commit()
        return res

    except sql.Error as err:
        print(err)
        return -1

    finally:
        cursor.close()


def fetchCart(loginid):
    _cart = "SELECT * FROM CartView WHERE ordid = '{}'".format(loginid)
    cart = execute(_cart)
    cart_total = 0
    for item in cart:
        cart_total += item[2]
    return cart, cart_total


@user.route('/')
def index():
    if 'user' in session and session['user']:
        loginid, usertype = session['user']

        customer_details = "SELECT * FROM Customer WHERE uid = '{}'".format(loginid)
        order_history = "SELECT * FROM Corders WHERE uid = '{}' AND totalCost != 0".format(loginid)

        customer = execute(customer_details)[0]
        order = execute(order_history)

        cart, cart_total = fetchCart(loginid)

        if order == -1 or customer == -1 or cart == -1:
            return render_template('error-404.html')
        else:
            return render_template('my-account.html', Customer=customer, Orders=order, Cart=cart, CartTotal=cart_total)
    else:
        return redirect('/auth')


@user.route('/order<int:oid>')
def orders(oid):
    _order = "SELECT * FROM Corders WHERE cordid = '{}'".format(oid)
    order = execute(_order)

    if order == -1 or len(order) != 1:
        return render_template('error-404.html')

    if 'user' in session and session['user']:
        uid = session['user'][0]

        if str(order[0][1]) != str(uid):
            return redirect('/auth/logout')

        customer_details = "SELECT * FROM Customer WHERE uid = '{}'".format(uid)
        customer = execute(customer_details)[0]

        _incart = "SELECT * FROM InCartView WHERE ordid = '{}'".format(oid)
        incart = execute(_incart)

        cart, cart_total = fetchCart(uid)

        _transaction = "SELECT * FROM Transactions WHERE cordid = '{}'".format(oid)
        transaction = execute(_transaction)

        if incart == -1 or transaction == -1 or customer == -1 or cart == -1:
            return render_template('error-404.html')
        return render_template('order.html', Customer=customer, Order=order[0], Carts=incart, Transactions=transaction, Cart=cart, CartTotal=cart_total)

    else:
        return redirect('/auth')


@user.route('/update', methods=['POST'])
def update():
    if 'user' in session and session['user']:
        loginid, usertype = session['user']
        fname = request.form['firstname']
        lname = request.form['lastname']
        phone = request.form['phone']
        email = request.form['email']
        gender = request.form['gender']
        dob = request.form['birthdate']
        hno = request.form['hno']
        street = request.form['street']
        district = request.form['district']
        state = request.form['state']
        pincode = request.form['pincode']

        query = "UPDATE Customer SET fname = '{}', lname = '{}', phone = '{}', email = '{}', gender = '{}'," \
                " dob = '{}', hno = {}, street='{}', district='{}', state='{}', pincode={}" \
                " WHERE uid = {}".format(fname, lname, phone, email, gender, dob, hno,
                                         street, district, state, pincode, loginid)
        res = execute(query)
        if res == -1:
            flash('Could not update the details')
        else:
            flash(' Details Updated Successfully')

        return redirect(request.referrer)
    else:
        return redirect('/auth')


@user.route('/cart')
def cart():
    if 'user' in session and session['user']:
        loginid, usertype = session['user']

        cart, cart_total = fetchCart(loginid)

        if cart == -1:
            return render_template('error-404.html')

        return render_template('cart.html', Carts=cart, CartTotal=cart_total)
    else:
        return redirect('/auth')


@user.route('/cartload', methods=['POST'])
def cartload():
    if 'user' in session and session['user']:
        loginid, usertype = session['user']
        pdid = request.form['pdid']
        attr = request.form['attribute']
        quantity = request.form['quantity']

        _price = "SELECT sellingPrice FROM Products WHERE pdid = '{}'".format(pdid)
        price = execute(_price)[0][0]

        subtotal = price * int(quantity)
        query = "INSERT INTO Cart (ordid, pdid, quantity, subtotal, attr, placed) VALUES ('{}', '{}', '{}', '{}', " \
                "'{}', '{}')".format(loginid, pdid, quantity, subtotal, attr, 0)
        res = execute(query)

        if res == -1:
            flash('Could not add to cart')
            return redirect(request.referrer)
        else:
            flash('Added to cart')
            return redirect(request.referrer)

    else:
        return redirect('/auth')


@user.route('/cartremove', methods=['POST'])
def cartremove():
    if 'user' in session and session['user']:
        loginid, usertype = session['user']
        pdid = request.form['pdid']
        quantity = request.form['quantity']
        attr = request.form['attr']
        placed = request.form['placed']

        query = "DELETE FROM Cart WHERE ordid = '{}' AND pdid = '{}' AND attr = '{}' AND placed = {} " \
                "AND quantity = {}".format(loginid, pdid, attr, placed, quantity)
        res = execute(query)

        if res == -1:
            flash('Could not remove from cart')
            print(res)
            return redirect(request.referrer)
        else:
            flash('Removed from cart')
            print("else", res)
            return redirect(request.referrer)

    else:
        return redirect('/auth')


@user.route('/checkout')
def checkout():
    if 'user' in session and session['user']:
        loginid, usertype = session['user']

        customer_details = "SELECT * FROM Customer WHERE uid = '{}'".format(loginid)
        customer = execute(customer_details)[0]

        cart, cart_total = fetchCart(loginid)

        _order = "SELECT * FROM OrderView WHERE ordid = '{}'".format(loginid)
        order = execute(_order)

        if cart == -1 or order == -1:
            flash('Could not fetch cart')
            return redirect('/cart')

        carttotal = 0
        for item in order:
            carttotal += item[1]

        return render_template('checkout.html', Customer=customer, Orders=order, Total=carttotal, Cart=cart, CartTotal=cart_total)

    else:
        return redirect('/auth')


@user.route('/placeorder', methods=['POST'])
def placeOrder():
    if 'user' in session and session['user']:
        loginid, usertype = session['user']
        paymentmethod = request.form['option']

        _subtotal = "SELECT Cart.subtotal " \
                    "FROM Cart WHERE Cart.ordid='{}'".format(loginid)
        subtotal = execute(_subtotal)

        if len(subtotal) == 0:
            flash('No items in cart')
            return redirect('/user/cart')

        total = 0
        for sub in subtotal:
            total += sub[0]

        print(total)
        query = "INSERT INTO Corders (uid, dateoforderplaced, dateoforderdelivery, orderstatus, totalCost) " \
                "VALUES ('{}', '{}', '{}', '{}', '{}')".format(loginid, date.today(), date.today() +
                                                               timedelta(days=random.randint(4, 8)), 0, total)
        res = execute(query)

        _ordid = "select max(cordid) from Corders"
        ordid = execute(_ordid)[0][0]

        _pending = "SELECT * FROM Cart WHERE ordid = '{}'".format(loginid)
        placed = execute(_pending)

        for item in placed:
            _update = "INSERT INTO Cart (ordid, pdid, quantity, subtotal, attr, placed)" \
                      "VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(ordid, item[1], item[2], item[3], item[4], 1)
            execute(_update)

        _delete = "DELETE FROM Cart WHERE ordid = '{}'".format(loginid)
        execute(_delete)

        _transactinn = "INSERT INTO Transactions (cordid, ofStatus, paymentmethod)" \
                       " VALUES ('{}', '{}', '{}')".format(ordid, 1, paymentmethod)
        execute(_transactinn)

        _allot = """INSERT INTO DeliveryPerson (cordid, deid) VALUES
                    ((select max(cordid) from Corders),
                    (SELECT eid FROM DeliveryPersonView 
                    ORDER BY RAND()
                    LIMIT 1))"""
        execute(_allot)

        print(res, ordid, placed)
        if res == -1 or placed == -1:
            flash('Could not place order')
            return redirect(request.referrer)
        else:
            flash('Order placed')
            return redirect('/user/order{}'.format(ordid))

    else:
        return redirect('/auth')
