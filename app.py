import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import flask_admin as admin
from flask_security import SQLAlchemyUserDatastore, Security, UserMixin, RoleMixin
from flask_security.utils import encrypt_password

app = Flask(__name__)
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
        return self.first_name

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


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

admin = admin.Admin(app, 'ezzTracker Admin', template_mode="bootstrap3")

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

        test_user = user_datastore.create_user(
            first_name='Admin',
            email='admin',
            password=encrypt_password('admin'),
            company_id=1,
            roles=[user_role, super_user_role]
        )

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
            user_datastore.create_user(
                first_name=first_names[i],
                last_name=last_names[i],
                email=tmp_email,
                password=encrypt_password(tmp_pass),
                roles=[user_role, ]
            )
        db.session.commit()
    return

@app.route('/')
def index():
    return '<h1>Pagina inicial</h1>'

if __name__ == '__main__':

    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])

    print database_path
    if not os.path.exists(database_path):
        build_ezztracker_db()

    # Start app
    app.run(debug=True)
