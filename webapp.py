import datetime
from flask import Flask, render_template, request, make_response, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import or_
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from data import db_session
from data.jobs import Jobs
from data.users import User
from data.register import RegisterForm
from data.login import LoginForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
param_index = dict()
param_index['title'] = 'Заготовка'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """Загрузка пользователя"""
    db = db_session.create_session()
    return db.query(User).get(user_id)


@app.route('/')
@app.route('/index')
@app.route(f'/index/{param_index["title"]}')
def index():
    """Корневая страница"""
    return render_template('list_prof.html', list='ul')


@app.route('/training/врач')
def training_doctor():
    return render_template('prof.html', type='Научные симуляторы')


@app.route('/training/инженер')
@app.route('/training/строитель')
def training_ingeneer():
    return render_template('prof.html', type='Инженерные тренажеры')


@app.route('/list_prof/ul')
def list_prof_ul():
    return render_template('list_prof.html', list='ul')


@app.route('/list_prof/ol')
def list_prof_ol():
    return render_template('list_prof.html', list='ol')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    """Страница регистрации"""
    regform = RegisterForm()
    if regform.validate_on_submit():
        if regform.password.data != regform.password_again.data:
            return render_template('register.html',
                                   title='Регистрация',
                                   form=regform,
                                   message='Пароли не совпадают')
        db = db_session.create_session()
        if db.query(User).filter(User.email == regform.email.data).first():
            return render_template('register.html',
                                   title='Регистрация',
                                   form=regform,
                                   message='Такой пользователь уже есть')
        user = User(name=regform.name.data,
                    email=regform.email.data)
        user.set_password(regform.password.data)
        db.add(user)
        db.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=regform)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Авторизация"""
    form = LoginForm()
    if form.validate_on_submit():
        db = db_session.create_session()
        user = db.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    """Выход из аккаунта"""
    logout_user()
    return redirect('/')


if __name__ == '__main__':
    db_session.global_init('db/mars.sqlite')
    app.run(host='localhost', port=5000)
