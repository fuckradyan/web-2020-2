from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from app import mysql

bp = Blueprint('auth', __name__, url_prefix='/auth')




class User(UserMixin):
    def __init__(self, user_id, login):
       super().__init__()
       self.id = user_id
       self.login = login 


def load_user(user_id):
    cursor =  mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT * FROM users WHERE id = %s;', (user_id,))
    db_user = cursor.fetchone()
    cursor.close()
    if db_user:
        return User(user_id=db_user.id, login=db_user.login)        
    return None   
 


@bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        remember_me = request.form.get('remember-me') == 'on'
        if login and password:
                cursor =  mysql.connection.cursor(named_tuple=True)
                cursor.execute('SELECT * FROM users WHERE login = %s AND password_hash = SHA2(%s, 256);', (login, password))
                db_user = cursor.fetchone()
                cursor.close()
                if db_user:
                    user = User(user_id=db_user.id, login=db_user.login) 
                    login_user(user, remember=remember_me)

                    flash('Вы успешно аутентифицированы', 'success')
                    next = request.args.get('next')
                    return redirect(next or url_for('index'))

        flash('Введены неверные логин и/или пароль.', 'danger')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view= 'auth.login'
    login_manager.login_message= 'Для доступа необходимо пройти процедуру аутентификации'
    login_manager.login_message_category= 'warning'
    login_manager.user_loader(load_user)