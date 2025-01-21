# Standard Library imports

# Core Flask imports
from flask import Blueprint, render_template

# Third-party imports

# App imports
from app import db_manager
from app import login_manager
from .views import (
    error_views,
    account_management_views,
    static_views,
)
from .models import User

bp = Blueprint('routes', __name__)

# alias
db = db_manager.session

# Request management
@bp.before_app_request
def before_request():
    db()

from flask_wtf import FlaskForm
from wtforms import StringField, validators
from .models import Person
from flask import request, redirect, url_for

class FormPerson(FlaskForm):
    name = StringField('Name', [
        validators.InputRequired(),
        validators.Length(max=30),
        validators.Regexp(r'^[a-zA-Z0-9 ]*$', message="Only ASCII characters without punctuation are allowed.")
    ])
    surname = StringField('Surname', [
        validators.InputRequired(),
        validators.Length(max=30),
        validators.Regexp(r'^[a-zA-Z0-9 ]*$', message="Only ASCII characters without punctuation are allowed.")
    ])
    email = StringField('Email', [
        validators.InputRequired(),
        validators.Length(max=50),
        validators.Email(message="Invalid email address.")
    ])
    
@bp.route("/person", methods=["GET", "POST"])
def formular():
    form = FormPerson()
    if form.validate_on_submit():
        new_person = Person(name=form.name.data, surname=form.surname.data, email=form.email.data)
        db.add(new_person)
        db.commit()
        return redirect(url_for('routes.success'))
    else:
        return render_template("formularPerson.html", form=form)
    
@bp.route("/success", methods=["GET", "POST"])
def success():
    return render_template("index.html", welcome_message="Welcome to Flask for", content_message="Rcord saved to database")


@bp.route("/persons", methods=["GET", "POST"])
def list_persons():
    if request.method == "POST":
        selected_ids = request.form.getlist("selected_ids")
        if selected_ids:
            Person.query.filter(Person.person_id.in_(selected_ids)).delete(synchronize_session=False)
            db.commit()
            return redirect(url_for("routes.list_persons"))
    
    persons = Person.query.all()
    return render_template("list_persons.html", persons=persons)

@bp.teardown_app_request
def shutdown_session(response_or_exc):
    db.remove()

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    if user_id and user_id != "None":
        return User.query.filter_by(user_id=user_id).first()

# Error views
bp.register_error_handler(404, error_views.not_found_error)

bp.register_error_handler(500, error_views.internal_error)

# Public views
@bp.route("/", methods=["GET", "POST"])
def index():
    welcome_message = "Welcome to Flask for Startups"
    content_message = "Content goes here..."
    return render_template('index.html', welcome_message=welcome_message, content_message=content_message)

bp.add_url_rule("/register", view_func=static_views.register)

bp.add_url_rule("/test", view_func=static_views.test)


bp.add_url_rule("/login", view_func=static_views.login)

# Login required views
bp.add_url_rule("/settings", view_func=static_views.settings)

# Public API
bp.add_url_rule(
   "/api/login", view_func=account_management_views.login_account, methods=["POST"]
)

bp.add_url_rule("/logout", view_func=account_management_views.logout_account)

bp.add_url_rule(
   "/api/register",
   view_func=account_management_views.register_account,
   methods=["POST"],
)

# Login Required API
bp.add_url_rule("/api/user", view_func=account_management_views.user)

bp.add_url_rule(
   "/api/email", view_func=account_management_views.email, methods=["POST"]
)

# Admin required
bp.add_url_rule("/admin", view_func=static_views.admin)
