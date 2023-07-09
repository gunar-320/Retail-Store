from flask import Blueprint, render_template, session, request, redirect, flash
import mysql.connector as sql

admin = Blueprint('admin', __name__, url_prefix='/admin',
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
        print("error", err)
        return -1


@admin.route('/')
def index():
    if 'user' in session and len(session['user']) > 0:
        if session['user'][1] != 'manager' and session['user'][1] != 'employee':
            return redirect('/adAuth/logout')

        else:
            loginid, usertype = session['user']

            if usertype == 'manager':
                return redirect('/manager')

            elif usertype == 'employee':
                if execute("SELECT COUNT(*) FROM CatHead WHERE cheid = {}".format(loginid))[0][0] > 0:
                    usertype = 'catHead'
                    session.clear()
                    session['user'] = (loginid, usertype)
                    return redirect('/catHead')

                elif execute("SELECT COUNT(*) FROM Worker WHERE weid = {}".format(loginid))[0][0] > 0:
                    usertype = 'worker'
                    session.clear()
                    session['user'] = (loginid, usertype)
                    return redirect('/worker')

                elif execute("SELECT  COUNT(*) FROM DeliveryPerson WHERE deid = {}".format(loginid))[0][0] > 0:
                    usertype = 'deliveryPerson'
                    session.clear()
                    session['user'] = (loginid, usertype)
                    return redirect('/deliveryPerson')

    else:
        return redirect("/adAuth")
