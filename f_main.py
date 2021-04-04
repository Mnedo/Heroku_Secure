from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import abort
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import PasswordField, BooleanField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
import os
from data.users import User
from flask import Flask, render_template, request
from data import db_session
from data.news import News
from data.jobs import Jobs
from data.category import Category, association_table
from data.depatment import Department
from data.forms.news import NewsForm
from data.forms.deps import DepsForm
from data.forms.user import RegisterForm
from data.forms.jobs import JobsForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

db_session.global_init("db/blogs.db")
db_sess = db_session.create_session()

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
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
    logout_user()
    return redirect("/")


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/jobs', methods=['GET', 'POST'])
@login_required
def add_jobs():
    form = JobsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = Jobs()
        k = len(db_sess.query(Jobs).all())
        jobs.id = k + 1
        jobs.team_leader = form.team_leader.data
        jobs.job = form.job.data
        jobs.work_size = form.work_size.data
        jobs.is_finished = form.is_finished.data
        jobs.collaborators = form.collaborators.data
        current_user.jobs.append(jobs)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('jobs.html', form=form, title="Добавление работы")


@app.route("/")
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != True)
    jobs = db_sess.query(Jobs).all()
    return render_template("index.html", news=news, jobs=jobs)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            speciality=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/jobs/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_jobs(id):
    form = JobsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).get(id)
        if jobs:
            form.team_leader.data = jobs.team_leader
            form.job.data = jobs.job
            form.work_size.data = jobs.work_size
            form.is_finished.data = jobs.is_finished
            form.collaborators.data = jobs.collaborators
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).get(id)
        if jobs:
            jobs.team_leader = form.team_leader.data
            jobs.job = form.job.data
            jobs.work_size = form.work_size.data
            jobs.is_finished = form.is_finished.data
            jobs.collaborators = form.collaborators.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('jobs.html',
                           title='Редактирование работы',
                           form=form
                           )


@app.route('/jobs_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def jobs_delete(id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).filter(Jobs.id == id).first()
    if jobs:
        db_sess.delete(jobs)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


######################
@app.route('/departments')
@login_required
def departments():
    db_sess = db_session.create_session()
    deps = db_sess.query(Department).all()
    return render_template('departments_main.html', deps=deps)


@app.route('/departments_', methods=['GET', 'POST'])
@login_required
def add_dep():
    form = DepsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        dep = Department()
        dep.title = form.title.data
        dep.members = form.members.data
        dep.chief = form.chief.data
        dep.email = form.email.data
        current_user.department.append(dep)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/departments')
    return render_template('departments.html', form=form, title="Добавление департамента")


@app.route('/departments_/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_dep(id):
    form = DepsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        dep = db_sess.query(Department).get(id)
        if dep:
            form.title.data = dep.title
            form.members.data = dep.members
            form.chief.data = dep.chief
            form.email.data = dep.email
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        dep = db_sess.query(Department).get(id)
        if dep:
            dep.title = form.title.data
            dep.members = form.members.data
            dep.chief = form.chief.data
            dep.email = form.email.data
            db_sess.commit()
            return redirect('/departments')
        else:
            abort(404)
    return render_template('departments.html',
                           title='Редактирование департамента',
                           form=form
                           )


@app.route('/departments_del/<int:id>', methods=['GET', 'POST'])
@login_required
def dep_delete(id):
    db_sess = db_session.create_session()
    dep = db_sess.query(Department).get(id)
    if dep:
        db_sess.delete(dep)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/departments')


@app.route('/works_log', methods=['GET', 'POST'])
@login_required
def work_log():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    category = db_sess.query(Category).all()
    categ = {}
    for el in category:
        for sc in db_sess.query(association_table).all():
            if sc[1] == el.id:
                idd = el.name
            categ[sc[0]] = idd
    return render_template('work_log.html', title="Work log", jobs=jobs, cat=categ)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
