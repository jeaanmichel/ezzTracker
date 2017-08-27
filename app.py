import os
from flask import Flask, url_for, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from wtforms import form, fields, validators
import flask_admin as admin
import flask_login as login
from flask_security import SQLAlchemyUserDatastore, Security, UserMixin, RoleMixin
from flask_admin.contrib import sqla
from flask_admin import helpers, expose
from werkzeug.security import generate_password_hash, check_password_hash
from flask_security.utils import encrypt_password


# Create Flask application
app = Flask(__name__)

# Create dummy secrey key so we can use sessions
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey("user.id")),
    db.Column('role_id', db.Integer(), db.ForeignKey("role.id"))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255), unique=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(100))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    telephone = db.Column(db.String(50), nullable=True)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    company = db.relationship('Company', backref=db.backref('user_company'))


    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __unicode__(self):
        return self.email

    def __str__(self):
        return self.email


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(50))
    description = db.Column(db.Text, nullable=True)

    def __str__(self):
        return self.company_name


class Os(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    initials = db.Column(db.String(50))
    version = db.Column(db.String(50))

    def __str__(self):
        return self.name + " " + self.version


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    initials = db.Column(db.String(50))
    version = db.Column(db.String(50))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    os_id = db.Column(db.Integer, db.ForeignKey('os.id'))
    company = db.relationship('Company', backref=db.backref('products_company'))
    os = db.relationship('Os', backref=db.backref('products_os'))

    def __str__(self):
        return self.initials + " " + self.version


class Priority(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __str__(self):
        return self.name


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __str__(self):
        return self.name


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    priority_id = db.Column(db.Integer, db.ForeignKey('priority.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    description = db.Column(db.Text)
    priority = db.relationship('Priority', backref=db.backref('track_priority'))
    product = db.relationship('Products', backref=db.backref('track_product'))
    requester = db.relationship('User', backref=db.backref('track_requester'))
    status = db.relationship('Status', backref=db.backref('track_status'))

    def __str__(self):
        return "#" + str(self.id) + " - " + self.title


class TrackHandler(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    handler_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tracker_id = db.Column(db.Integer, db.ForeignKey('track.id'))
    handler = db.relationship('User', backref=db.backref('trackhandler_handler'))
    tracker = db.relationship('Track', backref=db.backref('trackhandler_tracker'))
    handle_at = db.Column(db.DateTime())


# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    email = fields.StringField(validators=[validators.required()])
    senha = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Email invalido')

        if not check_password_hash(user.password, self.senha.data):
            raise validators.ValidationError('Senha invalida')

    def get_user(self):
        return db.session.query(User).filter_by(email=self.email.data).first()


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)


# Create customized index view class that handles login & registration
class MyAdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        link = ''
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


# Flask views
@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(403)
def page_not_found(e):
    return '<h1>HA HA! Vc nao tem autorizacao pra acessar esta pagina</h1>', 403


# Initialize flask-login
init_login()

# Create admin
admin = admin.Admin(app, 'ezzTracker Admin', index_view=MyAdminIndexView(), base_template='my_master.html')

from admin_views import *

admin.add_view(TrackView(Track, db.session))
admin.add_view(TrackHandlerView(TrackHandler, db.session))
admin.add_view(UserView(User, db.session))
admin.add_view(CompanyView(Company, db.session))
admin.add_view(ProductsView(Products, db.session))
admin.add_view(OsView(Os, db.session))
admin.add_view(StatusView(Status, db.session))
admin.add_view(PriorityView(Priority, db.session))


def build_ezztracker_db():
    """
    Populate a small db with some example entries.
    """

    import string
    import random

    db.drop_all()
    db.create_all()

    with app.app_context():

        company = Company(id=1, company_name=app.config['COMPANY_NAME'])
        db.session.add(company)

        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.commit()

        user = User(
            login='admin',
            first_name='Admin',
            email='admin@ebizz.com.br',
            password=generate_password_hash('admin'),
            company_id=1,
            roles=[user_role, super_user_role]
        )

        db.session.add(user)

        first_names = [
            'Harry', 'Amelia', 'Oliver', 'Jack', 'Isabella', 'Charlie', 'Sophie', 'Mia',
            'Jacob', 'Thomas', 'Emily', 'Lily', 'Ava', 'Isla', 'Alfie', 'Olivia', 'Jessica',
            'Riley', 'William', 'James', 'Geoffrey', 'Lisa', 'Benjamin', 'Stacey', 'Lucy'
        ]
        last_names = [
            'Brown', 'Smith', 'Patel', 'Jones', 'Williams', 'Johnson', 'Taylor', 'Thomas',
            'Roberts', 'Khan', 'Lewis', 'Jackson', 'Clarke', 'James', 'Phillips', 'Wilson',
            'Ali', 'Mason', 'Mitchell', 'Rose', 'Davis', 'Davies', 'Rodriguez', 'Cox', 'Alexander'
        ]

        for i in range(len(first_names)):
            tmp_email = first_names[i].lower() + "." + last_names[i].lower() + "@example.com"
            tmp_pass = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(10))
            user = User(
                first_name=first_names[i],
                last_name=last_names[i],
                email=tmp_email,
                password=generate_password_hash(tmp_pass),
                roles=[user_role, ]
            )
            db.session.add(user)
        db.session.commit()
    return

if __name__ == '__main__':

    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])

    print database_path
    if not os.path.exists(database_path):
        build_ezztracker_db()

    # Start app
    app.run(debug=True)