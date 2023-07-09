from flask import Flask, redirect
from store import store
from auth import auth
from user import user
from adAuth import adAuth
from admin import admin

from manager import manager
from worker import worker
from catHead import catHead
from deliveryPerson import deliveryPerson

app = Flask(__name__)
app.register_blueprint(store, url_prefix='/store')
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(user, url_prefix='/user')

app.register_blueprint(adAuth, url_prefix='/adAuth')
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(manager, url_prefix='/manager')
app.register_blueprint(worker, url_prefix='/worker')
app.register_blueprint(deliveryPerson, url_prefix='/deliveryPerson')
app.register_blueprint(catHead, url_prefix='/catHead')


app.secret_key = 'secret-key-JPAS'


@app.route('/')
def index():
    return redirect('/auth')


if __name__ == '__main__':
    app.run(debug=True)
