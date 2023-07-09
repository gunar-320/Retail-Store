from flask import Blueprint, render_template, session, request, redirect, flash
import mysql.connector as sql

deliveryPerson = Blueprint('deliveryPerson', __name__, url_prefix='/deliveryPerson', template_folder='templates_admin',
                           static_folder='templates_admin/assets')

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


@deliveryPerson.route('/')
def index():
    if 'user' in session and len(session['user']) > 0:
        print(len(session['user']))
        if session['user'][1] != 'deliveryPerson':
            return redirect('/adAuth/logout')
        else:
            loginid, usertype = session['user']
            _person = """SELECT * 
                       FROM Employee
                       WHERE eid = {}""".format(loginid)
            person = execute(_person)

            _order = """select * from Shippings WHERE deid = {}""".format(loginid)
            order = execute(_order)

            if order == -1:
                return render_template('error-404.html')

            return render_template('deliveryPerson.html', Person=person[0], Orders=order)
    else:
        return redirect('/admin')


@deliveryPerson.route('/update', methods=['POST'])
def update():
    if 'user' in session and len(session['user']) > 0:
        if session['user'][1] != 'deliveryPerson':
            return redirect('/adAuth/logout')
        else:
            loginid, usertype = session['user']
            fname = request.form['firstname']
            lname = request.form['lastname']
            phone = request.form['phone']
            email = request.form['email']
            dob = request.form['birthdate']
            gender = request.form['gender']
            hno = request.form['hno']
            street = request.form['street']
            district = request.form['district']
            city = request.form['city']
            state = request.form['state']
            pincode = request.form['pincode']

            query = "UPDATE Employee SET fname = '{}', lname = '{}', phone = '{}', email = '{}', gender = '{}'," \
                    " dob = '{}', hno = {}, street='{}', district='{}', city='{}', state='{}', pincode={}" \
                    " WHERE eid = {}".format(fname, lname, phone, email, gender, dob, hno,
                                             street, district, city, state, pincode, loginid)
            res = execute(query)
            if res == -1:
                flash('Could not update the details')
            else:
                flash(' Details Updated Successfully')

            return redirect(request.referrer)
    else:
        return redirect('/adAuth')


@deliveryPerson.route('/changeStatus', methods=['POST'])
def changeStatus():
    if 'user' in session and len(session['user']) > 0:
        if session['user'][1] != 'deliveryPerson':
            return redirect('/adAuth/logout')
        else:
            cordid = request.form['cordid']
            query = "UPDATE Corders SET orderstatus = true WHERE cordid = {}".format(cordid)
            res = execute(query)
            if res == -1:
                flash('Could not update the status')
            else:
                flash(' Status Updated Successfully')

            return redirect(request.referrer)
    else:
        return redirect('/adAuth')
