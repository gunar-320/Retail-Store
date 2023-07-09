from flask import Blueprint, render_template, session, request, redirect, flash
import mysql.connector as sql

adAuth = Blueprint('adAuth', __name__, url_prefix='/adAuth', template_folder='templates_admin',
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


@adAuth.route('/')
def index():
    if 'user' in session and len(session['user']) > 0:
        print(len(session['user']))
        if session['user'][1] != 'manager' and session['user'][1] != 'employee':
            return redirect('/adAuth/logout')
        else:
            return redirect('/admin')
    else:
        return render_template('alogin.html')


@adAuth.route('/login', methods=['POST'])
def login():
    if request.method == "POST":
        loginid = request.form.get('LoginID')
        userType = request.form.get('UserType')
        password = request.form.get('Password')

        query = "SELECT * FROM login WHERE loginID = '{}' AND usertype = '{}' AND pasword = '{}'"\
            .format(loginid, userType, password)

        res = execute(query)

        employee = [loginid, userType]

        if res == -1 or len(res) == 0:
            flash("Invalid credentials")
            return redirect('/adAuth')

        session['user'] = employee
        return redirect('/admin')

    return redirect('/adAuth')


@adAuth.route("/logout")
def logout():
    if 'user' in session and session['user']:
        session.pop('user')
    return redirect('/adAuth')


@adAuth.route('/about')
def about():
    return render_template('about-us.html')


@adAuth.route('/contact')
def contact():
    return render_template('contact-us.html')


@adAuth.route('/faq')
def faq():
    return render_template('faq.html')

