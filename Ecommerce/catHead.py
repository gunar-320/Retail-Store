from flask import Blueprint, render_template, session, request, redirect, flash
import mysql.connector as sql
from datetime import date

catHead = Blueprint('catHead', __name__, url_prefix='/catHead', template_folder='templates_admin',
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


@catHead.route('/')
def index():
    if 'user' in session and len(session['user']) > 0:
        print(len(session['user']))
        if session['user'][1] != 'catHead':
            return redirect('/adAuth/logout')
        else:
            loginid, usertype = session['user']
            _head = """SELECT * 
                       FROM Employee JOIN CatHead ON Employee.eid = CatHead.cheid
                       WHERE Employee.eid = {}""".format(loginid)
            head = execute(_head)

            _inventory = """SELECT * FROM InventoryViewCat WHERE eid = {}""".format(loginid)
            inventory = execute(_inventory)

            _ininventory = """SELECT DISTINCT * FROM InInventoryViewCat WHERE eid = {}""".format(loginid)
            ininventory = execute(_ininventory)

            _employee = """SELECT *FROM EmployeeUnderCat WHERE superviser_eid = {}""".format(loginid)
            employees = execute(_employee)

            _products = """SELECT * FROM ProductsUnderCat WHERE cheid = {}""".format(loginid)
            products = execute(_products)

            return render_template('categoryHead.html', CatHead=head[0], InInventory=ininventory,
                                   Inventory=inventory[0], Employees=employees, Products=products)
    else:
        return redirect('/admin')


@catHead.route('/update', methods=['POST'])
def update():
    if 'user' in session and len(session['user']) > 0:
        if session['user'][1] != 'catHead':
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


@catHead.route('/removeEmployee', methods=['POST'])
def removeEmployee():
    if 'user' in session and len(session['user']) > 0:
        if session['user'][1] != 'catHead':
            return redirect('/adAuth/logout')
        else:
            loginid, usertype = session['user']
            empid = request.form['employee_id']

            query = "DELETE FROM Worker WHERE weid = {}".format(empid)
            res1 = execute(query)
            query = 'DELETE FROM Employee WHERE eid = "{}"'.format(empid)
            res2 = execute(query)

            if res1 == -1 or res2 == -1:
                flash('Could not remove the employee')
            else:
                flash('Employee removed successfully')

            return redirect(request.referrer)
    else:
        return redirect('/adAuth')


@catHead.route('/addEmployee', methods=['POST'])
def addEmployee():
    if 'user' in session and len(session['user']) > 0:
        if session['user'][1] != 'catHead':
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
            speciality = 'Worker'
            doj = date.today()
            hno = request.form['hno']
            street = request.form['street']
            city = request.form['city']
            district = request.form['district']
            state = request.form['state']
            pincode = request.form['pincode']

            query = """INSERT INTO Employee(fname, lname, phone, email, dob, gender, hno, street, district, city, state, 
                    pincode, salary, experience, speciality, doj) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', 
                    '{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(fname, lname, phone, email, dob, gender, hno,
                                                                        street, district, city, state, pincode, salary,
                                                                        experience, speciality, doj)
            res1 = execute(query)
            if res1 == -1:
                return render_template("error-404.html")

            query = """INSERT INTO Supervisor (superviser_eid, supervisee_eid)
                        SELECT MAX(Employee.eid) AS supervisee_eid, CatHead.cheid as superviser_eid
                        FROM Employee, CatHead
                        WHERE CatHead.cheid = '{}'""".format(loginid)
            res2 = execute(query)

            if res2 == -1:
                return render_template("error-404.html")

            query = """INSERT INTO Worker (weid, catid)
                        SELECT MAX(Employee.eid) AS weid, CatHead.catid as catid
                        FROM Employee, CatHead
                        WHERE CatHead.cheid = '{}'""".format(loginid)
            res3 = execute(query)

            if res1 == -1 or res2 == -1 or res3 == -1:
                flash('Could not add the employee')
            else:
                flash('Employee added successfully')

            return redirect(request.referrer)
    else:
        return redirect('/adAuth')


@catHead.route('/updateSalary', methods=['POST'])
def updateSalary():
    if 'user' in session and len(session['user']) > 0:
        if session['user'][1] != 'catHead':
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


@catHead.route('/addProduct', methods=['POST'])
def addProduct():
    if 'user' in session and len(session['user']) > 0:
        if session['user'][1] != 'catHead':
            return redirect('/adAuth/logout')
        else:
            loginid, usertype = session['user']

            _catid = "Select catid from CatHead where cheid = '{}'".format(loginid)
            catid = execute(_catid)[0][0]

            name = request.form['name']
            brand = request.form['brand']
            image = 'http://dummyimage.com/157x100.png'
            type = request.form['type']
            costPrice = request.form['costPrice']
            rating = request.form['rating']
            query1 = """INSERT INTO Products (catid, name, brand, images, oftype, costPrice, rating)
                    VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(catid, name, brand, image, type,
                                                                               costPrice, rating)
            execute(query1)
            _pdid = "SELECT MAX(pdid) FROM Products"
            pdid = execute(_pdid)[0][0]

            # extra attributes
            if str(catid) == "1":
                color = request.form['color']
                gender = request.form['gender']
                size = request.form['size']
                quantity = request.form['quantity']

                query2 = """INSERT INTO Clothes (pdid, color, gender, size, quantity) VALUES
                ('{}', '{}', '{}', '{}', '{}')""".format(pdid, color, gender, size, quantity)
                res = execute(query2)

                if res == -1:
                    return render_template("error-404.html")  # error page

            elif str(catid) == "2":
                color = request.form['color']
                gender = request.form['gender']
                size = request.form['size']
                quantity = request.form['quantity']
                query2 = """INSERT INTO Footwears (pdid, color, gender, size, quantity) VALUES
                                ('{}', '{}', '{}', '{}', '{}')""".format(pdid, color, gender, size, quantity)
                res = execute(query2)
                if res == -1:
                    return render_template("error-404.html")  # error page

            else:
                mfgDate = request.form['mfg']
                quantity = request.form['quantity']
                query2 = """INSERT INTO Eappliances (pdid, mfgDate, quantity) VALUES
                            ('{}', '{}', '{}')""".format(pdid, mfgDate, quantity)
                res = execute(query2)
                print("hi5")
                if res == -1:
                    return render_template("error-404.html")  # error page

            if res == -1:
                flash('Could not add the product')
            else:
                flash('Product added successfully')

            return redirect(request.referrer)


@catHead.route('/updatePrice', methods=['POST'])
def updatePrice():
    if 'user' in session and len(session['user']) > 0:
        if session['user'][1] != 'catHead':
            return redirect('/adAuth/logout')
        else:
            pdid = request.form['pdid']
            price = request.form['price']
            query = "UPDATE Products SET costPrice = {} WHERE pdid = {}".format(price, pdid)
            res = execute(query)
            if res == -1:
                flash('Could not update the price')
            else:
                flash(' Price Updated Successfully')

            return redirect(request.referrer)
    else:
        return redirect('/adAuth')


@catHead.route('/deleteProduct', methods=['POST'])
def deleteProduct():
    if 'user' in session and len(session['user']) > 0:
        if session['user'][1] != 'catHead':
            return redirect('/adAuth/logout')
        else:
            pdid = request.form['pdid']
            query = "DELETE FROM Products WHERE pdid = {}".format(pdid)
            res = execute(query)

            if res == -1:
                flash('Could not delete the product')
            else:
                flash('Product deleted successfully')
            return redirect(request.referrer)
    else:
        return redirect('/adAuth')

