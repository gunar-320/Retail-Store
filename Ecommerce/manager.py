from flask import Blueprint, render_template, session, request, redirect, flash
import mysql.connector as sql
from datetime import date

manager = Blueprint('manager', __name__, url_prefix='/manager',
                    template_folder='templates_admin', static_folder='templates_admin/assets')

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


@manager.route('/')
def index():
    if 'user' in session and len(session['user']) > 0:
        if session['user'][1] != 'manager':
            return redirect('/adAuth/logout')
        else:
            loginid, usertype = session['user']

            _manager = "SELECT * FROM Manager WHERE meid = '{}'".format(loginid)
            managers = execute(_manager)

            _inventory = "SELECT * FROM Inventory WHERE invenid = '{}'".format(managers[0][1])
            inventory = execute(_inventory)

            _ininventory = "SELECT * FROM InInventoryViewMan Where invenid = '{}'".format(managers[0][1])
            ininventory = execute(_ininventory)

            _vendors = "SELECT * FROM VendorViewMan WHERE invenid = '{}'".format(managers[0][1])
            vendors = execute(_vendors)

            _employee = """SELECT E1.eid, E1.fname, E1.lname, E1.phone,  J.job, E1.salary
                            FROM Employee E1, (
                                    SELECT  E2.eid,
                                    CASE
                                        WHEN E2.eid IN (SELECT DISTINCT deid FROM DeliveryPerson) THEN 'Delivery Person'
                                        ELSE 'Category Head'
                                    END AS job
                                    FROM Employee E2 JOIN Supervision ON E2.eid = Supervision.eid
                                    WHERE Supervision.meid = '{}'
                                 ) J
                            WHERE E1.eid = J.eid""".format(loginid)

            employees = execute(_employee)

            if manager == -1 or inventory == -1 or ininventory == -1 or vendors == -1 or employees == -1:
                return render_template('error-404.html')

            return render_template('manager.html', Manager=managers[0], Inventory=inventory[0],
                                   InInventory=ininventory, Vendors=vendors, Employees=employees)

    else:
        return redirect('/adAuth/login')


@manager.route('/update', methods=['POST'])
def update():
    if 'user' in session and len(session['user']) > 0:
        if session['user'][1] != 'manager':
            return redirect('/adAuth/logout')
        else:
            loginid, usertype = session['user']
            fname = request.form['firstname']
            lname = request.form['lastname']
            phone = request.form['phone']
            email = request.form['email']
            gender = request.form['gender']
            dob = request.form['birthdate']
            hno = request.form['hno']
            street = request.form['street']
            city = request.form['city']
            district = request.form['district']
            state = request.form['state']
            pincode = request.form['pincode']

            query = "UPDATE Manager SET fname = '{}', lname = '{}', phone = '{}', email = '{}', gender = '{}'," \
                    " dob = '{}', hno = {}, street='{}', city='{}', district='{}', state='{}', pincode={}" \
                    " WHERE meid = {}".format(fname, lname, phone, email, gender, dob, hno,
                                              street, district, city, state, pincode, loginid)
            res = execute(query)
            if res == -1:
                flash('Could not update the details')
            else:
                flash(' Details Updated Successfully')

            return redirect(request.referrer)
    else:
        return redirect('/auth')


@manager.route('/add', methods=['POST'])
def add():
    if 'user' in session and len(session['user']) > 0:
        if session['user'][1] != 'manager':
            return redirect('/adAuth/logout')
        else:
            pdid = request.form['product_id']
            invenid = request.form['inventory_id']

            query = "INSERT INTO InInventory (invenid, pdid) VALUES ('{}', '{}')".format(invenid, pdid)
            res = execute(query)

            if res == -1:
                flash('Could not add the product')
            else:
                flash('Product added successfully')

            return redirect(request.referrer)
    else:
        return redirect('/auth')


@manager.route('/remove', methods=['POST'])
def remove():
    if 'user' in session and len(session['user']) > 0:
        if session['user'][1] != 'manager':
            return redirect('/adAuth/logout')
        else:
            pdid = request.form['product_id']
            invenid = request.form['inventory_id']

            query = "DELETE FROM InInventory WHERE invenid = '{}' AND pdid = '{}'".format(invenid, pdid)
            res = execute(query)

            if res == -1:
                flash('Could not remove the product')
            else:
                flash('Product removed successfully')

            return redirect(request.referrer)
    else:
        return redirect('/adAuth')


@manager.route('/order', methods=['POST'])
def order():
    if 'user' in session and len(session['user']) > 0:
        if session['user'][1] != 'manager':
            return redirect('/adAuth/logout')
        else:
                invenid = request.form['inventory_id']
                pdid = request.form['product_id']
                quantity = request.form['quantity']

                _quantity = """SELECT quantity FROM InInventory WHERE invenid = '{}' AND pdid = '{}'""".format(invenid, pdid)
                quant = execute(_quantity)[0][0]
                quantity = int(quantity) + quant

                query = """UPDATE InInventory SET quantity = '{}'
                            WHERE invenid = '{}' AND pdid = '{}'""".format(quantity, invenid, pdid)
                res = execute(query)

                _venid = """SELECT venid FROM Vendor 
                            ORDER BY RAND()
                            LIMIT 1"""
                venid = execute(_venid)[0][0]

                _distributes = """INSERT IGNORE INTO Distributes(invenid, venid) VALUES ({}, {})""".format(invenid, venid)
                distributes = execute(_distributes)

                _invoice = """INSERT INTO Invoice(invenid, statusof, receivedDate, fulfilledDate) VALUES
                                ('{}', '1', '{}', '{}')""".format(invenid, date.today(), date.today())
                invoice = execute(_invoice)

                _morders = """INSERT INTO Morders(invid, venid)
                                SELECT MAX(Invoice.invid) AS invid,'{}' as venid
                                    FROM Invoice""".format(venid)
                morders = execute(_morders)

                _invid = """SELECT MAX(Invoice.invid)"""
                invid = execute(_invid)

                _batch = """INSERT INTO Batch(pdid, invid, quantity) Values 
                            ({}, (SELECT MAX(Invoice.invid) FROM Invoice), {})""".format(pdid, quant)
                batch = execute(_batch)

                if res == -1 or quant == -1 or venid == -1 or distributes == -1 or invoice == -1 or morders == -1 or batch == -1 or invid == -1:
                    return render_template('error-404.html')

                if res == -1:
                    flash('Could not place the order')
                else:
                    flash('Order placed successfully')

                return redirect(request.referrer)
    else:
        return redirect('/auth')


@manager.route('/viewOrder', methods=['POST'])
def viewOrder():
    if 'user' in session and len(session['user']) > 0:
        if session['user'][1] != 'manager':
            return redirect('/adAuth/logout')
        else:
            invenid = request.form['inventory_id']
            venid = request.form['vendor_id']

            _inven = "SELECT * FROM Inventory WHERE invenid = '{}'".format(invenid)
            _ven = "SELECT * FROM Vendor WHERE venid = '{}'".format(venid)
            _invoices = "SELECT * FROM InvoiceUnderMan WHERE venid = '{}' AND invenid = '{}'".format(venid, invenid)
            _batch = "SELECT * FROM BatchView WHERE venid = '{}' AND invenid = '{}'".format(venid, invenid)

            inven = execute(_inven)
            ven = execute(_ven)
            invoices = execute(_invoices)
            batch = execute(_batch)

            return render_template("aorder.html", Inventory=inven[0], Vendor=ven[0], Invoices=invoices, Batch=batch)
    else:
        return redirect('/auth')


@manager.route('/removeEmployee', methods=['POST'])
def removeEmployee():
    if 'user' in session and len(session['user']) > 0:
        if session['user'][1] != 'manager':
            return redirect('/adAuth/logout')
        else:
            loginid, usertype = session['user']
            empid = request.form['employee_id']

            query = "DELETE FROM  CatHead WHERE cheid = '{}'".format(empid)
            res1 = execute(query)
            query = 'DELETE FROM Employee WHERE eid = "{}"'.format(empid, loginid)
            res2 = execute(query)

            if res1 == -1 or res2 == -1:
                flash('Could not remove the employee')
            else:
                flash('Employee removed successfully')

            return redirect(request.referrer)
    else:
        return redirect('/auth')


@manager.route('/addEmployee', methods=['POST'])
def addEmployee():
    if 'user' in session and len(session['user']) > 0:
        if session['user'][1] != 'manager':
            return redirect('/adAuth/logout')
        else:
            loginid, usertype = session['user']
            fname = request.form['firstname']
            lname = request.form['lastname']
            phone = request.form['phone']
            email = request.form['email']
            dob = request.form['birthdate']
            gender = request.form['gender']
            salary = request.form['salary']
            experience = request.form['experience']
            speciality = request.form['speciality']
            doj = date.today()
            hno = request.form['hno']
            street = request.form['street']
            city = request.form['city']
            district = request.form['district']
            state = request.form['state']
            pincode = request.form['pincode']
            position = request.form['position']

            query = """INSERT INTO Employee(fname, lname, phone, email, dob, gender, hno, street, district, city, state, 
                                pincode, salary, experience, speciality, doj) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', 
                                '{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(fname, lname, phone, email, dob,
                                                                                    gender, hno,
                                                                                    street, district, city, state,
                                                                                    pincode, salary,
                                                                                    experience, speciality, doj)
            res1 = execute(query)
            if res1 == -1:
                return render_template("error-404.html")

            query = """INSERT INTO Supervision (eid, meid)
                                    SELECT MAX(Employee.eid) AS eid, {} as meid
                                    FROM Employee""".format(loginid)
            res2 = execute(query)
            if str(position) is not '0':
                query = """INSERT INTO CatHead (cheid, catid)
                                    SELECT MAX(Employee.eid) AS cheid, '{}' as catid
                                    FROM Employee""".format(position)
                res3 = execute(query)
                if res3 == -1:
                    return render_template("error-404.html")

            if res1 == -1 or res2 == -1:
                flash('Could not add the employee')
            else:
                flash('Employee added successfully')

            return redirect(request.referrer)
    else:
        return redirect('/auth')


@manager.route('/updateSalary', methods=['POST'])
def updateSalary():
    if 'user' in session and len(session['user']) > 0:
        if session['user'][1] != 'manager':
            return redirect('/adAuth/logout')
        else:

            salary = request.form['salary']
            empid = request.form['employee_id']

            query = "UPDATE Employee SET salary = '{}' WHERE eid = '{}'".format(salary, empid)
            res = execute(query)

            if res == -1:
                flash('Could not update the salary')
            else:
                flash('Salary updated successfully')

            return redirect(request.referrer)
    else:
        return redirect('/adAuth')
