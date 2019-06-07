from slugify import slugify

from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, current_user,
                         logout_user, login_required)
from flask import (Flask, render_template, flash, redirect,
                   url_for, g, abort, request)

from peewee import *

import models
import forms
import pep8

checker = pep8.Checker("app.py")

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = "Shh..."

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


def admin():
    try:
        models.User.create_user(username="admin",
                                email="admin@admin.com",
                                password="password",
                                admin=True)
    except ValueError:
        pass


@login_manager.user_loader
def load_user(user_id):
    try:
        return models.User.get(models.User.id == user_id)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/')
@app.route("/entries")
@app.route("/entries/tag/<tag>")
def index(tag=None):
    if tag:
        entries = models.Journal.select().where(
            (models.Journal.tags == tag) |
            (models.Journal.tags.contains(tag)))
    else:
        entries = models.Journal.select().limit(10)
    return render_template('index.html', entries=entries, title="Home")


@app.route("/register", methods=("GET", "POST"))
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = forms.RegistrationForm()
    if form.validate_on_submit():
        models.User.create_user(username=form.username.data.lower(),
                                email=form.email.data.lower(),
                                password=form.password.data)

        flash("You have successfully registered!", "success")
        return redirect(url_for("login"))
    return render_template('register.html',
                           form=form,
                           title="Register")


@app.route("/login", methods=("GET", "POST"))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = forms.LoginForm()
    if form.validate_on_submit():
        user = models.User.get(email=form.email.data)
        if user and check_password_hash(
                user.password, form.password.data):

            login_user(user, remember=form.remember_me.data)
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Login failed. Please check email and password.",
                  "danger")

    return render_template('login.html', form=form, title="Login")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/entries/new", methods=("GET", "POST"))
@login_required
def new_entry():
    form = forms.JournalEntry()
    if form.validate_on_submit():
        models.Journal.create(
            title=form.title.data.strip(),
            date=form.date.data,
            time_spent=form.time_spent.data,
            what_you_learned=form.what_you_learned.data.strip(),
            resources_to_remember=form.resources_to_remember.data.strip(),
            slug=slugify(form.title.data.strip()),
            user_id=g.user._get_current_object(),
            tags=form.tags.data.strip().lower()
        )

        flash("Entry added!", "success")
        return redirect(url_for("index"))
    return render_template('new.html', form=form, title="New Entry")


@app.route("/entries/<slug>")
@login_required
def detail(slug):
    try:
        entry = models.Journal.select().where(
            models.Journal.slug == slug).get()

        resources = entry.resources_to_remember.split(", ")
        tags = entry.tags.split(", ")
        return render_template('detail.html', entry=entry,
                               title=entry.title, resources=resources,
                               tags=tags)
    except DoesNotExist:
        abort(404)


@app.route("/entries/<slug>/edit", methods=("GET", "POST"))
@login_required
def edit(slug):
    try:
        entry = models.Journal.select().where(
            models.Journal.slug == slug).get()

        form = forms.JournalEntry()

        if entry.user_id != current_user:
            abort(403)

        if form.validate_on_submit():
            entry.title = form.title.data
            entry.date = form.date.data
            entry.time_spent = form.time_spent.data
            entry.what_you_learned = form.what_you_learned.data
            entry.resources_to_remember = form.resources_to_remember.data
            entry.slug = slugify(form.title.data)
            entry.tags = form.tags.data
            entry.save()
            flash("Entry updated!", "success")
            return redirect(url_for('index'))

        elif request.method == 'GET':
            form.title.data = entry.title
            form.date.data = entry.date
            form.time_spent.data = entry.time_spent
            form.what_you_learned.data = entry.what_you_learned
            form.resources_to_remember.data = entry.resources_to_remember
            form.tags.data = entry.tags
        return render_template('edit.html', entry=entry,
                               form=form, title="Edit")

    except DoesNotExist:
        abort(404)


@app.route("/entries/<slug>/delete", methods=("GET", "POST"))
@login_required
def delete(slug):
    try:
        entry = models.Journal.select().where(
            models.Journal.slug == slug).get()

        if entry.user_id != current_user:
            abort(403)

        entry.delete_instance()
        flash("Entry deleted!", "success")
        return redirect(url_for("index"))
    except DoesNotExist:
        abort(404)


if __name__ == '__main__':
    models.initialize()
    admin()
    app.run(debug=DEBUG, host=HOST, port=PORT)
