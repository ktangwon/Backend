from flask import current_app as app

from flask import request, jsonify
from flask_login import LoginManager, login_user, logout_user, current_user
import bcrypt
from flask_login.utils import login_required
from sqlalchemy.exc import IntegrityError
from .models import Users


from .query import read_queries, write_queries

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    print("pass")
    return Users.query.get(int(user_id))

# THIS IS A DUMMY THING COPIED FROM AJ KANAT


@app.route('/login', methods=['GET'])
def get_login():
    return '''
               <form action='api/login' method='POST'>
                <input type='text' name='username' id='username' placeholder='username'/>
                <input type='password' name='password' id='password' placeholder='password'/>
                <input type='submit' name='submit'/>
               </form>
            '''

@app.route('/api/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if (username != None and password != None):
        passwordToByte = password.encode('utf8')

        encrypted_password = read_queries.get_encrypted_password(username)
        # print(encrypted_password)
        # print(type(encrypted_password))
        # print(type(bcrypt.hashpw(passwordToByte, bcrypt.gensalt(10))))

        if (encrypted_password != None):
            # only uncomment when testing (in case we manually add password without encrypt lol)
            # encrypted_password = bcrypt.hashpw(str.encode(encrypted_password), bcrypt.gensalt(10))
            if (bcrypt.checkpw(passwordToByte, encrypted_password.encode('utf8'))):
                current_user = Users.query.filter(Users.username == username).first()
                login_user(current_user, remember=True)
                return jsonify(username=username, status=True, message="Login successfully")
    return jsonify(username="", status=False, message="Can not login")

@app.route('/api/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    sky_user = request.form.get('sky_username')
    mod = request.form.get('mod')

    if (username != None and password != None and sky_user != None):
        if mod == None:
            mod = False
        try:
            write_queries.register_client(sky_user,username,password, mod)
        except (IntegrityError):
            return jsonify(username=username, status=False, message="Username or sky username already taken")
        return jsonify(username=username, status=True, message="Register successfully")
    return jsonify(username=username, status=False, message="Username, password and sky username cannot be empty")
    

@app.route('/api/logout', methods=['GET','POST'])
def logout():
    user = None
    try:
        user = current_user.username
    except (AttributeError):
        return jsonify(status=False, username="", message="User hasnt logged in yet")
    logout_user()
    return jsonify(status=True, username=user, message="Logout successfully")

@app.route('/api/test', methods=['GET'])
def test():
    try:
        return "Login as " + str(current_user.username)
    except (AttributeError):
        return "Not login yet"

